import React from 'react';
import { CopyBlock,dracula} from "react-code-blocks";
import style from './CodeBlock.module.css';
import { FaCode } from "react-icons/fa6";

const CodeBlock = ({ language, value }) => {
    const customTheme = {
        ...dracula,
        // backgroundColor: "transparent", // Transparent background
        // textColor: "#EDEDED", // Light text color 
        // keywordColor: "#FF5F5F", // Light red for keywords (e.g., `const`, `let`)
        // stringColor: "#76C7C0",  // Light teal for strings
        // numberColor: "#F78C6C",  // Light orange for numbers
        // commentColor: "#A6ACCD", // Light gray for comments
        // variableColor: "#C0A9E3", // Light purple for variables
        // functionColor: "#82C1D4", // Light cyan for function names
      };
    return (
        <div className={style.container}>
            <div className={style.headingContainer}>
              <span className={style.heading}> <FaCode/> {language}</span>
              <span className={style.heading}>Copy</span>
            </div>
          
        <div className={style.codeblock}>
            <CopyBlock
                language={language}
                text={value}
                showLineNumbers={false}
                theme={customTheme}
                wrapLines={true}
                codeBlock
            />     
          </div>
        </div>
    );
}

export default CodeBlock;
