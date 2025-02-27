import React from 'react';
import { CopyBlock, dracula, github } from "react-code-blocks";
import styles from './CodeBlock.module.css';

const CodeBlock = ({ language, value, isHighlighted, editorColor = false, isStreaming }) => {
  return (
    <div className={`${styles.container} ${isHighlighted ? styles.highlighted : ''}`}>
      <div className={styles.codeWrapper}>
        <CopyBlock
          language={language}
          text={value}
          showLineNumbers={true}
          theme={editorColor === true ? dracula : github}
          wrapLines={true}
          codeBlock
        />
        {isStreaming && (
          <span className={styles.codeCursor} />
        )}
      </div>
    </div>
  );
};

export default CodeBlock;