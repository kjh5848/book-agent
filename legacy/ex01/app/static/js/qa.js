/**
 * Q&A 실시간 채팅 로직 (AJAX)
 */
const chatHistory = document.getElementById('chatHistory');
const loadingIndicator = document.getElementById('loadingIndicator');
const queryInput = document.getElementById('queryInput');

function scrollToBottom() {
    if (chatHistory) {
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }
}

/**
 * 채팅 내역을 localStorage에 저장
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
    
    localStorage.setItem('metacoding_chat_history', JSON.stringify(messages));
}

/**
 * localStorage에서 채팅 내역 로드
 */
function loadChatHistory() {
    const saved = localStorage.getItem('metacoding_chat_history');
    if (!saved || !chatHistory) return;
    
    try {
        const messages = JSON.parse(saved);
        chatHistory.innerHTML = ''; // 초기화 후 다시 채움
        messages.forEach(msg => {
            const div = document.createElement('div');
            div.className = msg.className;
            div.innerHTML = msg.innerHTML;
            chatHistory.appendChild(div);
        });
        scrollToBottom();
    } catch (e) {
        console.error("Failed to load chat history:", e);
    }
}

/**
 * 채팅 내력 비우기
 */
function clearChatHistory() {
    if (confirm("대화 내역을 모두 지우시겠습니까?")) {
        localStorage.removeItem('metacoding_chat_history');
        if (chatHistory) chatHistory.innerHTML = '';
    }
}

async function submitQuery(event) {
    if (event) event.preventDefault(); // 폼 기본 제출 방지

    const query = queryInput.value.trim();
    if (!query) return;

    // 1. 사용자 메시지 추가
    // ... (기존 로직 유지)
    const userMsgDiv = document.createElement('div');
    userMsgDiv.className = 'chat-message user-message';
    userMsgDiv.innerHTML = `<div class="message-content">${query}</div>`; // XSS 방지를 위해 textContent 권장하나 기존 유지
    userMsgDiv.querySelector('.message-content').textContent = query; // 안전하게 텍스트만 삽입
    chatHistory.appendChild(userMsgDiv);
    
    // 입력창 초기화
    queryInput.value = '';
    
    // ... (이하 로직 동일)
    saveChatHistory();
    scrollToBottom();

    // 2. 로딩 표시 및 AI 답변 준비
    loadingIndicator.style.display = 'flex';

    try {
        const isAgentMode = document.getElementById('agentModeToggle').checked;
        const endpoint = isAgentMode ? '/admin/qa/agent' : '/admin/qa/query';

        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query: query })
        });

        if (!response.ok) throw new Error('서버 응답 오류');

        const data = await response.json();
        
        // 3. AI 답변 표시
        const aiMsgDiv = document.createElement('div');
        aiMsgDiv.className = 'chat-message ai-message';
        
        let content = data.answer || "답변을 가져올 수 없습니다.";
        // 줄바꿈 처리
        content = content.replace(/\n/g, '<br />');
        
        aiMsgDiv.innerHTML = `
            <div class="avatar">🤖</div>
            <div class="message-content">
                <div class="ai-ans-text">${content}</div>
                ${data.mode === 'agent' ? '<small style="color:#666; display:block; margin-top:10px;">⚡ Agent Mode 실행됨</small>' : ''}
                
                ${renderSourceAccordion(data)}
            </div>
        `;
        
        chatHistory.appendChild(aiMsgDiv);
        saveChatHistory();

    } catch (error) {
        console.error('Error:', error);
        const errorDiv = document.createElement('div');
        errorDiv.className = 'chat-message ai-message';
        errorDiv.innerHTML = `
            <div class="avatar">⚠️</div>
            <div class="message-content">오류가 발생했습니다. 다시 시도해 주세요. (${error.message})</div>
        `;
        chatHistory.appendChild(errorDiv);
        saveChatHistory();
    } finally {
        loadingIndicator.style.display = 'none';
        scrollToBottom();
    }
}

// 초기 로드 시 내역 불러오기 및 스크롤
window.addEventListener('DOMContentLoaded', () => {
    // 저장된 내역이 있으면 불러와서 표시 (기존 SSR 내용 덮어쓰기)
    const saved = localStorage.getItem('metacoding_chat_history');
    if (saved) {
        loadChatHistory();
    }
    scrollToBottom();
});

// 이벤트 리스너 수정
// 폼 제출 이벤트로 통일 (엔터키도 기본적으로 폼 제출을 트리거함)
const qaForm = document.getElementById('qaForm');
if (qaForm) {
    qaForm.addEventListener('submit', submitQuery);
}

// 기존 엔터키 리스너 제거 (필요 없음)
// window load 시 리스너 등록 방식 변경

/**
 * 근거 데이터(Reference) 아코디언 HTML 생성
 */
function renderSourceAccordion(data) {
    // 데이터가 없으면 빈 문자열 반환
    const hasUnstructured = data.unstructured_data && data.unstructured_data.length > 0;
    const hasStructured = data.structured_data && (
        (data.structured_data.employees && data.structured_data.employees.length > 0) ||
        (data.structured_data.leaves && data.structured_data.leaves.length > 0) ||
        (data.structured_data.sales && data.structured_data.sales.length > 0)
    );

    if (!hasUnstructured && !hasStructured) {
        return '';
    }

    // 문서 검색 결과 HTML 생성
    let uniqueDocs = [];
    if (hasUnstructured) {
        // 중복 제거 (내용 기준)
        const seen = new Set();
        data.unstructured_data.forEach(doc => {
            if (!seen.has(doc.content)) {
                seen.add(doc.content);
                uniqueDocs.push(doc);
            }
        });
    }

    let unstructuredHtml = '';
    if (uniqueDocs.length > 0) {
        unstructuredHtml = uniqueDocs.map(doc => `
            <div class="source-item">
                <small>${doc.source || '문서 검색'}</small>
                <p>${doc.content.substring(0, 150)}...</p>
            </div>
        `).join('');
    } else {
        unstructuredHtml = '<p class="no-data">관련 문서 없음</p>';
    }

    // DB 조회 결과 HTML 생성
    let structuredHtml = '';
    if (hasStructured) {
        const sd = data.structured_data;
        
        if (sd.employees && sd.employees.length > 0) {
            structuredHtml += `
                <div class="source-item">
                    직원 정보: ${sd.employees.length}명 조회됨
                    <small>(${sd.employees.slice(0, 3).map(e => e.name).join(', ')} 등)</small>
                </div>
            `;
        }
        
        if (sd.leaves && sd.leaves.length > 0) {
            structuredHtml += `
                <div class="source-item">
                    휴가 정보 조회됨 (${sd.leaves.length}건)
                </div>
            `;
        }
        
        if (sd.sales && sd.sales.length > 0) {
            const total = sd.sales.reduce((sum, s) => sum + (s.amount || 0), 0);
            structuredHtml += `
                <div class="source-item">
                    매출 정보 조회됨 (총 ${total.toLocaleString()}원)
                </div>
            `;
        }
    }
    
    if (!structuredHtml) {
        structuredHtml = '<p class="no-data">DB 조회 내역 없음</p>';
    }

    // 아코디언 전체 HTML 반환
    return `
        <div class="source-container">
            <div class="source-header" onclick="this.parentElement.classList.toggle('active')">
                <span>🔍 분석 근거 보기 (Reference Data)</span>
                <i class="arrow">▼</i>
            </div>
            <div class="source-body">
                <div class="source-grid">
                    <div class="source-column">
                        <h5>📚 문서 검색 결과</h5>
                        ${unstructuredHtml}
                    </div>
                    <div class="source-column">
                        <h5>📊 데이터베이스 조회</h5>
                        ${structuredHtml}
                    </div>
                </div>
            </div>
        </div>
    `;
}
