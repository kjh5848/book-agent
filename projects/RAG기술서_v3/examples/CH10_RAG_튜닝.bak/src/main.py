"""CH10 RAG 튜닝 - 통합 실행 진입점.

모든 튜닝 실험을 순서대로 실행하거나 개별 실험을 선택하여 실행합니다.
각 실험은 ChromaDB 없이 인메모리 샘플 데이터로 독립 실행 가능합니다.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

# 프로젝트 루트를 sys.path에 추가
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv()

console = Console()

# 사용 가능한 실험 목록
EXPERIMENTS = {
    "1": {
        "name": "청킹 전략 실험",
        "description": "Fixed-size vs Semantic 청킹 비교, 크기/오버랩 실험",
        "module": "tuning.chunk_experiment",
        "func": "run_all_experiments"
    },
    "2": {
        "name": "Retriever 튜닝 실험",
        "description": "k값(3/5/10), Threshold, Metadata Filtering 실험",
        "module": "tuning.retriever_experiment",
        "func": "run_all_retriever_experiments"
    },
    "3": {
        "name": "ReRanker 실험",
        "description": "Cross-Encoder 기반 top_k=20 → top_k=5 재정렬",
        "module": "tuning.reranker",
        "func": "run_reranker_experiment"
    },
    "4": {
        "name": "하이브리드 검색 실험",
        "description": "BM25 + Vector EnsembleRetriever, alpha 파라미터 실험",
        "module": "tuning.hybrid_search",
        "func": "run_hybrid_search_experiment"
    },
    "5": {
        "name": "고급 Retriever 실험",
        "description": "ParentDocument, SelfQuery, ContextualCompression 비교",
        "module": "tuning.advanced_retriever",
        "func": "run_advanced_retriever_experiment"
    },
    "6": {
        "name": "Query Rewrite 실험",
        "description": "HyDE, Multi-Query, 약어/동의어 확장",
        "module": "tuning.query_rewrite",
        "func": "run_query_rewrite_experiment"
    },
    "7": {
        "name": "Vision + OCR 하이브리드 추출",
        "description": "LLaVA 이미지 캡션 + EasyOCR 텍스트 추출",
        "module": "tuning.vision_extractor",
        "func": "run_vision_extractor_demo"
    },
    "8": {
        "name": "평가 프레임워크 데모",
        "description": "Precision@k, Recall@k, 환각률, before/after 비교",
        "module": "src.eval_framework",
        "func": "run_full_evaluation_demo"
    },
    "all": {
        "name": "전체 실험 순서 실행",
        "description": "모든 실험을 1~8 순서로 실행",
        "module": None,
        "func": None
    }
}


def print_menu() -> None:
    """실험 선택 메뉴를 출력합니다."""
    console.rule("[bold blue]CH10 RAG 튜닝 - 실험 선택 메뉴[/bold blue]")
    console.print(
        "\n이 챕터에서는 RAG 품질을 개선하는 다양한 튜닝 기법을 실험합니다.\n"
        "각 실험은 ChromaDB 없이 인메모리 샘플 데이터로 독립 실행 가능합니다.\n"
    )

    table = Table(title="사용 가능한 실험 목록")
    table.add_column("번호", style="cyan", justify="center")
    table.add_column("실험 이름", style="bold white")
    table.add_column("설명", style="dim white")

    for key, exp in EXPERIMENTS.items():
        table.add_row(key, exp["name"], exp["description"])

    console.print(table)


def run_experiment(experiment_key: str) -> None:
    """선택한 실험을 실행합니다.

    Args:
        experiment_key: 실험 키 ("1"~"8" 또는 "all")
    """
    if experiment_key not in EXPERIMENTS:
        console.print(f"[red]잘못된 선택입니다: {experiment_key}[/red]")
        console.print(f"유효한 선택지: {', '.join(EXPERIMENTS.keys())}")
        return

    if experiment_key == "all":
        run_all_experiments()
        return

    exp = EXPERIMENTS[experiment_key]
    module_name = exp["module"]
    func_name = exp["func"]

    console.print(
        f"\n[bold green]실험 {experiment_key}: {exp['name']} 시작[/bold green]"
    )

    try:
        import importlib
        module = importlib.import_module(module_name)
        func = getattr(module, func_name)
        func()

    except ModuleNotFoundError as e:
        console.print(f"[red]모듈을 찾을 수 없습니다: {e}[/red]")
        console.print("requirements.txt에 따라 패키지를 설치하십시오:")
        console.print("  pip install -r requirements.txt")

    except Exception as e:
        console.print(f"[red]실험 실행 중 오류 발생: {e}[/red]")
        raise


def run_all_experiments() -> None:
    """모든 실험을 순서대로 실행합니다."""
    console.rule("[bold magenta]전체 실험 순서 실행[/bold magenta]")
    console.print(
        "[yellow]주의: 전체 실행에는 임베딩 모델 다운로드로 인해 "
        "시간이 걸릴 수 있습니다.[/yellow]\n"
    )

    ordered_keys = ["1", "2", "3", "4", "5", "6", "7", "8"]

    for key in ordered_keys:
        exp = EXPERIMENTS[key]
        console.print(
            f"\n[bold cyan]{'='*50}[/bold cyan]"
            f"\n[bold]실험 {key}: {exp['name']}[/bold]"
        )
        run_experiment(key)


def check_environment() -> dict[str, bool]:
    """실행 환경을 점검합니다.

    Returns:
        패키지 설치 여부 딕셔너리
    """
    checks = {
        "python-dotenv": False,
        "rich": False,
        "langchain": False,
        "sentence-transformers": False,
        "rank-bm25": False,
        "chromadb": False,
        "easyocr": False,
        "pypdf": False,
    }

    for package in checks:
        try:
            import importlib
            pkg_name = package.replace("-", "_")
            importlib.import_module(pkg_name)
            checks[package] = True
        except ImportError:
            checks[package] = False

    return checks


def print_environment_check() -> None:
    """환경 점검 결과를 출력합니다."""
    console.rule("[bold]환경 점검[/bold]")
    checks = check_environment()

    table = Table(title="패키지 설치 현황")
    table.add_column("패키지", style="cyan")
    table.add_column("상태", style="bold")

    for package, installed in checks.items():
        status = "[green]설치됨[/green]" if installed else "[red]미설치[/red]"
        table.add_row(package, status)

    console.print(table)

    not_installed = [pkg for pkg, ok in checks.items() if not ok]
    if not_installed:
        console.print(
            f"\n[yellow]일부 패키지가 설치되지 않았습니다. "
            f"해당 실험은 폴백 모드로 동작합니다.[/yellow]"
        )
        console.print("전체 설치: pip install -r requirements.txt")


def main() -> None:
    """메인 실행 함수.

    명령줄 인수로 실험 번호를 전달하거나, 대화형으로 선택합니다.
    """
    # 환경 점검
    print_environment_check()

    # 메뉴 출력
    print_menu()

    # 명령줄 인수 처리
    if len(sys.argv) > 1:
        experiment_key = sys.argv[1].lower()
        console.print(f"\n[cyan]선택된 실험: {experiment_key}[/cyan]")
        run_experiment(experiment_key)
        return

    # 대화형 선택
    console.print(
        "\n실험 번호를 입력하십시오 (1~8) 또는 'all' (전체 실행): ",
        end=""
    )

    try:
        choice = input().strip().lower()
        if not choice:
            choice = "8"  # 기본값: 평가 프레임워크 데모

        run_experiment(choice)

    except KeyboardInterrupt:
        console.print("\n\n[yellow]실험이 취소되었습니다.[/yellow]")
        sys.exit(0)


if __name__ == "__main__":
    main()
