import CodeBlock from './CodeBlock/CodeBlock';
import Markdown from 'react-markdown'
import remarkGfm from 'remark-gfm';
import rehypeKatex from 'rehype-katex'
import remarkMath from 'remark-math'
import 'katex/dist/katex.min.css'
import style from './CodeBlock/CodeBlock.module.css'

const ResponseFormater = ({role, message }) => {
   
  return (
    <Markdown
      remarkPlugins={[remarkGfm, remarkMath]}
      rehypePlugins={[rehypeKatex]}
      children={message}
      components={{
        code({ node, inline, className, children, ...props }) 
        {
          const match = /language-(\w+)/.exec(className || '');

          return  match ? (
            <CodeBlock
              language={match[1]}
              value={String(children).replace(/\n$/, '')}
            />
          ) : (
            <code className={`${role === 'ai' ? style.highLiter : style.nonHighLiter}`} {...props}>
              {children}
            </code>
          );
        },
      }}
    />
  );
};

export default ResponseFormater;

