/**
 * qa.js — Q&A 채팅 비동기 처리 로직
 *
 * 기능:
 *   - 사용자 질문을 POST /admin/qa/query 로 전송
 *   - LLM 답변 및 출처 카드 렌더링
 *   - localStorage 기반 대화 내역 유지
 */

const chatHistory = document.getElementById('chatHistory');
const loadingIndicator = document.getElementById('loadingIndicator');
const queryInput = document.getElementById('queryInput');

/**
 * 채팅 영역을 최하단으로 스크롤합니다.
 */
function scrollToBottom() {
    if (chatHistory) {
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }
}

/**
 * 현재 대화 내역을 localStorage에 저장합니다.
 */
function saveChatHistory() {
    const messages = [];
    const messageElements = chatHistory.querySelectorAll('.chat-message');
    messageElements.forEach(el => {
        messages.push({
            className: el.className,
            innerHTML: el.innerHTML
        });
    });
    localStorage.setItem('rag_qa_chat_history', JSON.stringify(messages));
}

/**
 * localStorage에서 대화 내역을 불러와 화면에 렌더링합니다.
 */
function loadChatHistory() {
    const saved = localStorage.getItem('rag_qa_chat_history');
    if (!saved || !chatHistory) return;

    try {
        const messages = JSON.parse(saved);
        chatHistory.innerHTML = '';
        messages.forEach(msg => {
            const div = document.createElement('div');
            div.className = msg.className;
            div.innerHTML = msg.innerHTML;
            chatHistory.appendChild(div);
        });
        scrollToBottom();
    } catch (e) {
        console.error('대화 내역 로드 실패:', e);
    }
}

/**
 * 대화 내역을 초기화합니다. (localStorage 포함)
 */
function clearChatHistory() {
    if (confirm('대화 내역을 모두 지우시겠습니까?')) {
        localStorage.removeItem('rag_qa_chat_history');
        if (chatHistory) chatHistory.innerHTML = '';
    }
}

/**
 * 출처 카드 아코디언 HTML을 생성합니다.
 *
 * @param {Object} data - 서버 응답 객체 ({unstructured_data, route})
 * @returns {string} 아코디언 HTML 문자열
 */
function renderSourceAccordion(data) {
    const hasUnstructured = data.unstructured_data && data.unstructured_data.length > 0;

    if (!hasUnstructured) {
        return '';
    }

    // 중복 제거 (content 기준)
    const seen = new Set();
    const uniqueDocs = [];
    data.unstructured_data.forEach(doc => {
        if (!seen.has(doc.content)) {
            seen.add(doc.content);
            uniqueDocs.push(doc);
        }
    });

    const docsHtml = uniqueDocs.map(doc => {
        const source = doc.source || '출처 불명';
        const preview = doc.content.substring(0, 150) + (doc.content.length > 150 ? '...' : '');
        const score = typeof doc.score === 'number' ? doc.score.toFixed(2) : '-';
        return `
            <div class="source-item">
                <small>${source}</small>
                <p>${preview}</p>
                <div class="source-score">유사도: ${score}</div>
            </div>
        `;
    }).join('');

    const routeLabel = data.route || 'unstructured';

    return `
        <div class="route-badge">라우팅: ${routeLabel}</div>
        <div class="source-container">
            <div class="source-header" onclick="this.parentElement.classList.toggle('active')">
                <span>분석 근거 보기 (출처 문서)</span>
                <i class="arrow">&#9660;</i>
            </div>
            <div class="source-body">
                ${docsHtml}
            </div>
        </div>
    `;
}

/**
 * 폼 제출 이벤트 핸들러 — 질문을 서버로 전송하고 응답을 렌더링합니다.
 *
 * @param {Event} event - 폼 제출 이벤트
 */
async function submitQuery(event) {
    if (event) event.preventDefault();

    const query = queryInput.value.trim();
    if (!query) return;

    // 사용자 메시지 추가
    const userMsgDiv = document.createElement('div');
    userMsgDiv.className = 'chat-message user-message';
    const userContent = document.createElement('div');
    userContent.className = 'message-content';
    userContent.textContent = query;  // XSS 방지: textContent 사용
    userMsgDiv.appendChild(userContent);
    chatHistory.appendChild(userMsgDiv);

    queryInput.value = '';
    saveChatHistory();
    scrollToBottom();

    // 로딩 표시
    loadingIndicator.style.display = 'flex';

    try {
        const response = await fetch('/admin/qa/query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: query })
        });

        if (!response.ok) {
            const errData = await response.json().catch(() => ({}));
            throw new Error(errData.detail || `서버 오류 (${response.status})`);
        }

        const data = await response.json();

        // AI 답변 렌더링
        const aiMsgDiv = document.createElement('div');
        aiMsgDiv.className = 'chat-message ai-message';

        let answerHtml = (data.answer || '답변을 가져올 수 없습니다.')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/\n/g, '<br>');

        aiMsgDiv.innerHTML = `
            <div class="avatar">AI</div>
            <div class="message-content">
                <div class="ai-ans-text">${answerHtml}</div>
                ${renderSourceAccordion(data)}
            </div>
        `;

        chatHistory.appendChild(aiMsgDiv);
        saveChatHistory();

    } catch (error) {
        console.error('질문 처리 오류:', error);
        const errorDiv = document.createElement('div');
        errorDiv.className = 'chat-message ai-message';
        errorDiv.innerHTML = `
            <div class="avatar">!</div>
            <div class="message-content">오류가 발생했습니다: ${error.message}</div>
        `;
        chatHistory.appendChild(errorDiv);
        saveChatHistory();
    } finally {
        loadingIndicator.style.display = 'none';
        scrollToBottom();
    }
}

// 초기화 — 저장된 내역 로드
window.addEventListener('DOMContentLoaded', () => {
    const saved = localStorage.getItem('rag_qa_chat_history');
    if (saved) {
        loadChatHistory();
    }
    scrollToBottom();
});

// 폼 제출 이벤트 등록
const qaForm = document.getElementById('qaForm');
if (qaForm) {
    qaForm.addEventListener('submit', submitQuery);
}
