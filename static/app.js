const chatWindow = document.querySelector('#chat-window');
const form = document.querySelector('#chat-form');
const input = document.querySelector('#question-input');
const counter = document.querySelector('#character-count');
const sendButton = form.querySelector('.send-button');

function escapeHtml(value) {
  return value.replace(/[&<>"']/g, (character) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  })[character]);
}

function scrollToLatest() {
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

function addUserMessage(text) {
  const row = document.createElement('article');
  row.className = 'message-row user-row';
  row.innerHTML = `<div class="message-content"><div class="message-meta"><strong>You</strong><span>just now</span></div><div class="message-bubble user-bubble"><p>${escapeHtml(text).replace(/\n/g, '<br>')}</p></div></div><div class="user-avatar" aria-hidden="true">G</div>`;
  chatWindow.append(row);
  scrollToLatest();
}

function addTypingIndicator() {
  const row = document.createElement('article');
  row.className = 'message-row assistant-row typing-row';
  row.innerHTML = '<div class="bot-avatar"><span>✳</span></div><div class="message-content"><div class="message-meta"><strong>Helpdesk assistant</strong><span>thinking</span></div><div class="message-bubble typing-bubble"><i></i><i></i><i></i></div></div>';
  chatWindow.append(row);
  scrollToLatest();
  return row;
}

function addAssistantMessage(result) {
  const row = document.createElement('article');
  row.className = 'message-row assistant-row';
  const matchNote = result.matchedQuestion
    ? `<div class="matched-question"><span>↳</span> Answering: “${escapeHtml(result.matchedQuestion)}” <span class="confidence">${Math.round(result.confidence * 100)}% match</span></div>`
    : '';
  const suggestions = result.suggestions?.length
    ? `<div class="response-suggestions"><span>Try asking:</span>${result.suggestions.map((question) => `<button type="button" data-question="${escapeHtml(question)}">${escapeHtml(question)}</button>`).join('')}</div>`
    : '';
  row.innerHTML = `<div class="bot-avatar"><span>✳</span></div><div class="message-content"><div class="message-meta"><strong>Helpdesk assistant</strong><span>just now</span></div><div class="message-bubble assistant-bubble"><p>${escapeHtml(result.answer)}</p>${matchNote}${suggestions}</div></div>`;
  chatWindow.append(row);
  scrollToLatest();
}

async function sendQuestion(question) {
  const text = question.trim();
  if (!text || sendButton.disabled) return;
  addUserMessage(text);
  input.value = '';
  input.style.height = 'auto';
  counter.textContent = '0 / 500';
  sendButton.disabled = true;
  const typing = addTypingIndicator();
  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: text })
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'Something went wrong.');
    addAssistantMessage(result);
  } catch (error) {
    addAssistantMessage({ answer: error.message || 'I couldn’t connect just now. Please try again.' });
  } finally {
    typing.remove();
    sendButton.disabled = false;
    input.focus();
  }
}

form.addEventListener('submit', (event) => {
  event.preventDefault();
  sendQuestion(input.value);
});

input.addEventListener('input', () => {
  counter.textContent = `${input.value.length} / 500`;
  input.style.height = 'auto';
  input.style.height = `${Math.min(input.scrollHeight, 120)}px`;
});

input.addEventListener('keydown', (event) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    sendQuestion(input.value);
  }
});

document.addEventListener('click', (event) => {
  const suggestion = event.target.closest('[data-question]');
  if (suggestion) sendQuestion(suggestion.dataset.question);
});

document.querySelector('#clear-chat').addEventListener('click', () => {
  chatWindow.innerHTML = '<div class="day-divider"><span>TODAY</span></div><article class="message-row assistant-row"><div class="bot-avatar"><span>✳</span></div><div class="message-content"><div class="message-meta"><strong>Helpdesk assistant</strong><span>just now</span></div><div class="message-bubble welcome-bubble"><p>Fresh start! 👋 Ask me about orders, shipping, returns, payments, and more.</p><p>What would you like to know?</p></div></div></article>';
  input.focus();
});
