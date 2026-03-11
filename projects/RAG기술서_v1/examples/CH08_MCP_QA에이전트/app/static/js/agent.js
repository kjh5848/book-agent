/**
 * MCP Agent 채팅 UI — 비동기 질의 전송, 답변 및 steps 아코디언 렌더링.
 *
 * 엔드포인트: POST /admin/qa/agent
 * 응답 구조: { answer, steps: [{tool, input, output}], mode }
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
        sendAgentQuery();
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
        <div class="label">MCP Agent</div>
        <div class="loading-bubble">
            <span></span><span></span><span></span>
            <small class="ms-2 text-muted" style="font-size:0.75rem;">도구 실행 중...</small>
        </div>
    `;
    container.appendChild(div);
    scrollToBottom();
    return div;
}

/**
 * AI 답변 버블을 채팅 컨테이너에 추가합니다.
 *
 * @param {string} answer - MCP Agent 최종 답변 텍스트.
 */
function appendAnswerMessage(answer) {
    const container = document.getElementById("chat-container");
    const div = document.createElement("div");
    div.className = "chat-message assistant";
    div.innerHTML = `
        <div class="label"><i class="bi bi-robot me-1"></i>MCP Agent</div>
        <div class="bubble">${nl2br(escapeHtml(answer))}</div>
    `;
    container.appendChild(div);
    scrollToBottom();
}

/**
 * 도구 사용 기록 아코디언을 채팅 컨테이너에 추가합니다.
 *
 * 각 step은 아코디언으로 접고 펼 수 있으며,
 * 도구명 / 입력값 / 출력값을 표시합니다.
 *
 * @param {Array<{tool: string, input: string|object, output: string}>} steps - 도구 사용 기록.
 */
function appendStepsAccordion(steps) {
    if (!steps || steps.length === 0) return;

    const container = document.getElementById("chat-container");
    const stepsDiv = document.createElement("div");
    stepsDiv.className = "steps-section";

    // 섹션 제목 (클릭 시 전체 토글)
    const title = document.createElement("div");
    title.className = "section-title";
    title.innerHTML = `<i class="bi bi-tools"></i>도구 사용 기록 (${steps.length}단계) <i class="bi bi-chevron-down ms-1" id="steps-toggle-icon"></i>`;
    title.style.cursor = "pointer";
    stepsDiv.appendChild(title);

    // 아코디언 컨테이너
    const accordionContainer = document.createElement("div");
    accordionContainer.id = "steps-accordion-body";

    steps.forEach((step, idx) => {
        const toolName = escapeHtml(String(step.tool || "알 수 없음"));
        const inputText = typeof step.input === "object"
            ? JSON.stringify(step.input, null, 2)
            : String(step.input || "");
        const outputText = String(step.output || "");

        const stepEl = document.createElement("div");
        stepEl.className = "step-accordion";
        stepEl.innerHTML = `
            <div class="step-header" onclick="toggleStep('step-body-${idx}', 'step-icon-${idx}')">
                <span class="step-num text-muted" style="font-size:0.75rem;">Step ${idx + 1}</span>
                <span class="tool-badge">${toolName}</span>
                <i class="bi bi-chevron-down ms-auto" id="step-icon-${idx}" style="font-size:0.75rem;"></i>
            </div>
            <div class="step-body" id="step-body-${idx}">
                <div class="mb-2">
                    <small class="text-muted fw-semibold">입력값</small>
                    <pre>${escapeHtml(inputText)}</pre>
                </div>
                <div>
                    <small class="text-muted fw-semibold">실행 결과</small>
                    <pre>${escapeHtml(outputText)}</pre>
                </div>
            </div>
        `;
        accordionContainer.appendChild(stepEl);
    });

    // 제목 클릭 시 전체 토글
    title.addEventListener("click", () => {
        const body = document.getElementById("steps-accordion-body");
        const icon = document.getElementById("steps-toggle-icon");
        const isHidden = body.style.display === "none";
        body.style.display = isHidden ? "block" : "none";
        icon.className = isHidden
            ? "bi bi-chevron-up ms-1"
            : "bi bi-chevron-down ms-1";
    });

    stepsDiv.appendChild(accordionContainer);
    container.appendChild(stepsDiv);
    scrollToBottom();
}

/**
 * 개별 step 아코디언 항목을 토글합니다.
 *
 * @param {string} bodyId - 펼칠 step body 요소의 ID.
 * @param {string} iconId - 토글 아이콘 요소의 ID.
 */
function toggleStep(bodyId, iconId) {
    const body = document.getElementById(bodyId);
    const icon = document.getElementById(iconId);
    if (!body) return;

    const isOpen = body.classList.contains("open");
    body.classList.toggle("open", !isOpen);
    if (icon) {
        icon.className = isOpen
            ? "bi bi-chevron-down ms-auto"
            : "bi bi-chevron-up ms-auto";
        icon.style.fontSize = "0.75rem";
    }
}

/**
 * MCP Agent 서버에 질의를 전송하고 답변과 steps 아코디언을 렌더링합니다.
 *
 * POST /admin/qa/agent → {answer, steps, mode}
 */
async function sendAgentQuery() {
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
        const response = await fetch("/admin/qa/agent", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query }),
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Agent 실행 중 오류가 발생했습니다.");
        }

        const data = await response.json();
        loadingEl.remove();

        // --- Output ---
        appendAnswerMessage(data.answer);
        appendStepsAccordion(data.steps || []);

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
