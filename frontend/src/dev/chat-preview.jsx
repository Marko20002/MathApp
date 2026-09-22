// Development-only visual test harness. This adapter never contacts the backend
// or OpenAI. The production entry point does not import this module.
import React from 'react';
import ReactDOM from 'react-dom/client';
import { MemoryRouter } from 'react-router-dom';
import api from '../api';
import Solver from '../pages/Solver';
import '../index.css';

if (!import.meta.env.DEV) throw new Error('Preview is development-only');
let messages = [];
let conversation = null;
const analysis = {
  problem_id: 1, classification: { label: 'CALCULUS', model_version: 'preview-fixture', experimental: true,
    confidence: .86, scores: { CALCULUS: .86, PROBABILITY: .08, DISCRETE: .06 } },
  openai_subject: 'CALCULUS', final_answer: '\\(0\\)', provider_model: 'Offline fixture — no API calls',
  context: { mode: 'full', messages_sent: 0 }, usage: { input_tokens: 180, output_tokens: 120, cached_input_tokens: 0 },
  reference: { answer: '', label: '', reviewed_at: null },
};
api.defaults.adapter = async config => {
  let data;
  if (config.url === '/api/auth/me/') data = { username: 'Offline preview', is_staff: true };
  else if (config.url === '/api/solver/conversations/') data = { results: conversation ? [conversation] : [], next: null };
  else if (config.url.endsWith('/messages/')) data = { results: [...messages].reverse(), next: null };
  else if (config.url.endsWith('/reference/')) {
    data = { ...JSON.parse(config.data), reviewed_at: new Date().toISOString(), reviewed_by: 1 };
  } else if (config.url === '/api/solver/solve/') {
    const payload = typeof config.data === 'string' ? JSON.parse(config.data) : { content: 'Attached example' };
    const content = messages.length ? 'As the denominator grows, the fraction becomes smaller.\n\nFor example, \\(1/10 = 0.1\\), while \\(1/100 = 0.01\\).\n\nSo the value approaches **zero**.' :
      'The limit is **zero**.\n\n\\[\\lim_{x\\to\\infty}\\frac{1}{x}=0\\]\n\nAs \\(x\\) grows, its reciprocal gets closer to zero. It never reaches zero for a finite positive \\(x\\).\n\nTry asking **why**, or ask for a numerical example.';
    const pair = [{ id: messages.length + 1, sequence: messages.length, role: 'user', content: payload.content, analysis: {} },
      { id: messages.length + 2, sequence: messages.length + 1, role: 'assistant', content, analysis }];
    messages.push(...pair);
    conversation = { id: 1, title: 'Understanding a limit' };
    data = { conversation_id: 1, messages: pair };
  } else throw new Error('Unexpected preview request: ' + config.url);
  return { data, status: 200, statusText: 'OK', headers: {}, config };
};
ReactDOM.createRoot(document.getElementById('root')).render(<MemoryRouter><Solver /></MemoryRouter>);
