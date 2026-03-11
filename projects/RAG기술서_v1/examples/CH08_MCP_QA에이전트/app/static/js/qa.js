/**
 * RAG Q&A 채팅 UI — 비동기 질의 전송 및 응답 렌더링.
 *
 * 엔드포인트: POST /admin/qa/query
 * 응답 구조: { answer, route, unstructured_data: [{content, source, score}] }
 */

"use strict";

/**
 * 엔터 키 입력 시 질의를 전송합니다.
 *
 * @param {KeyboardEvent} event - 키보드 이벤트 객체.
 */
function handleKeyDown(event) {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendQuery();
    }
}

/**
 * 추천 질문 버튼 클릭 시 입력창에 텍스트를 채웁니다.
 *
 * @param {HTMLElement} btn - 클릭된 추천 질문 버튼 요소.
 */
function fillQuery(btn) {
    const input = document.getElementById("query-input");
    input.value = btn.textContent.trim();
    input.focus();
}

/**
 * 채팅 컨테이너를 최하단으로 스크롤합니다.
 */
function scrollToBottom() {
    const container = document.getElementById("chat-container");
    container.scrollTop = container.scrollHeight;
}

/**
 * 사용자 메시지 버블을 채팅 컨테이너에 추가합니다.
 *
 * @param {string} text - 사용자 입력 텍스트.
 */
function appendUserMessage(text) {
    const emptyState = document.getElementById("empty-state");
    if (emptyState) emptyState.remove();

    const container = document.getElementById("chat-container");
    const div = document.createElement("div");
    div.className = "chat-message user";
    div.innerHTML = `
        <div class="label">나</div>
        <div class="bubble">${escapeHtml(text)}</div>
    `;
    container.appendChild(div);
    scrollToBottom();
}

/**
 * 로딩 스피너 버블을 채팅 컨테이너에 추가합니다.
 *
 * @returns {HTMLElement} 추가된 로딩 메시지 요소.
 */
function appendLoadingMessage() {
    const container = document.getElementById("chat-container");
    const div = document.createElement("div");
    div.className = "chat-message assistant";
    div.id = "loading-message";
    div.innerHTML = `
        <div class="label">AI 비서</div>
        <div class="loading-bubble">
            <span></span><span></span><span></span>
        </div>
    `;
    container.appendChild(div);
    scrollToBottom();
    return div;
}

/**
 * AI 답변 버블과 출처 카드를 채팅 컨테이너에 추가합니다.
 *
 * @param {string} answer - LLM이 생성한 답변 텍스트.
 * @param {string} route - 인텐트 라우팅 결과 (unstructured | hybrid).
 * @param {Array<{content: string, source: string, score: number}>} sources - 검색 결과 목록.
 */
function appendAssistantMessage(answer, route, sources) {
    const container = document.getElementById("chat-container");

    // 경로 배지 생성
    const routeLabel = route === "unstructured" ? "문서 검색" : "하이브리드";
    const routeBadge = `<span class="route-badge ${route}"><i class="bi bi-signpost me-1"></i>${routeLabel}</span>`;

    const div = document.createElement("div");
    div.className = "chat-message assistant";
    div.innerHTML = `
        <div class="label">AI 비서 ${routeBadge}</div>
        <div class="bubble">${nl2br(escapeHtml(answer))}</div>
    `;
    container.appendChild(div);

    // 출처 카드 렌더링
    if (sources && sources.length > 0) {
        const sourcesDiv = document.createElement("div");
        sourcesDiv.className = "sources-section";
        sourcesDiv.innerHTML = `
            <div class="section-title">
                <i class="bi bi-files"></i>참고 문서 (${sources.length}건)
            </div>
        `;

        sources.forEach((item) => {
            const card = document.createElement("div");
            card.className = "source-card";
            const scorePercent = Math.round((1 - item.score) * 100);
            card.innerHTML = `
                <div class="source-name"><i class="bi bi-file-text me-1"></i>${escapeHtml(item.source)}</div>
                <div class="source-content">${escapeHtml(item.content)}</div>
                <div class="source-score">유사도: ${scorePercent}%</div>
            `;
            sourcesDiv.appendChild(card);
        });

        container.appendChild(sourcesDiv);
    }

    scrollToBottom();
}

/**
 * RAG Q&A 서버에 질의를 전송하고 응답을 렌더링합니다.
 *
 * POST /admin/qa/query → {answer, route, unstructured_data}
 */
async function sendQuery() {
    // --- Input ---
    const input = document.getElementById("query-input");
    const sendBtn = document.getElementById("send-btn");
    const query = input.value.trim();

    if (!query) return;

    // --- Process ---
    input.value = "";
    input.disabled = true;
    sendBtn.disabled = true;

    appendUserMessage(query);
    const loadingEl = appendLoadingMessage();

    try {
        const response = await fetch("/admin/qa/query", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query }),
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "서버 오류가 발생했습니다.");
        }

        const data = await response.json();
        loadingEl.remove();

        // --- Output ---
        appendAssistantMessage(
            data.answer,
            data.route,
            data.unstructured_data || []
        );

    } catch (err) {
        loadingEl.remove();
        appendErrorMessage(err.message);
    } finally {
        input.disabled = false;
        sendBtn.disabled = false;
        input.focus();
    }
}

/**
 * 오류 메시지 버블을 채팅 컨테이너에 추가합니다.
 *
 * @param {string} message - 오류 메시지 문자열.
 */
function appendErrorMessage(message) {
    const container = document.getElementById("chat-container");
    const div = document.createElement("div");
    div.className = "chat-message assistant";
    div.innerHTML = `
        <div class="label">시스템</div>
        <div class="bubble text-danger">
            <i class="bi bi-exclamation-circle me-1"></i>${escapeHtml(message)}
        </div>
    `;
    container.appendChild(div);
    scrollToBottom();
}

/**
 * HTML 특수 문자를 이스케이프합니다.
 *
 * @param {string} text - 이스케이프할 텍스트.
 * @returns {string} 이스케이프된 HTML 안전 문자열.
 */
function escapeHtml(text) {
    const div = document.createElement("div");
    div.appendChild(document.createTextNode(text));
    return div.innerHTML;
}

/**
 * 줄바꿈 문자를 HTML <br> 태그로 변환합니다.
 *
 * @param {string} text - 변환할 텍스트.
 * @returns {string} <br> 태그가 포함된 HTML 문자열.
 */
function nl2br(text) {
    return text.replace(/\n/g, "<br>");
}
