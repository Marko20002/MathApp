import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import remarkGfm from 'remark-gfm';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';

export default function MathText({ text = '' }) {
  // Support the tutor's LaTeX delimiters alongside Markdown dollar delimiters.
  const markdown = text.replace(/\\\[([\s\S]*?)\\\]/g, (_, math) => '\n\n$$\n' + math + '\n$$\n\n')
    .replace(/\\\(([\s\S]*?)\\\)/g, (_, math) => '$' + math + '$');
  return <div className="math-text"><ReactMarkdown remarkPlugins={[remarkGfm, remarkMath]}
    rehypePlugins={[[rehypeKatex, { strict: false, throwOnError: false, trust: false }]]}
    components={{ a: ({ children, ...props }) => <a {...props} target="_blank" rel="noopener noreferrer">{children}</a>,
                  img: ({ alt }) => <span>{alt || '[Image]'}</span> }}>
    {markdown}
  </ReactMarkdown></div>;
}
