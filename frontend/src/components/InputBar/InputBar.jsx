import React, { useEffect, useRef, useState } from 'react';
import styles from './InputBar.module.css';
import { FaFolderPlus } from "react-icons/fa";
import { Tooltip } from 'antd';
import { FcOpenedFolder } from "react-icons/fc";


const InputBar = ({ input, setInput, handleSend, isLoading }) => {
    const inputRef = useRef(null);
    const [filePath, setFilePath] = useState(""); 
    const [folderName, setFolderName] = useState("");

    // const handleFilePathChange = (e) => {
    //     console.log(e)
    //     const file = e.target.files[0];
    //     if (file) {
    //         console.log(file)
    //         setFilePath(file.path || file.name); 
    //     }
    // };
    const handleFilePathChange = (event) => {
        const files = event.target.files;
        if (files.length > 0) {
          const firstFilePath = files[0].webkitRelativePath;
          const folder = firstFilePath.split("/")[0]; // Extracts folder name
          setFolderName(folder);
        }
      };



    const adjustHeight = () => {
        if (inputRef.current) {
            inputRef.current.style.height = '1.7rem';
            const scrollHeight = inputRef.current.scrollHeight;
            const maxHeight = parseInt(getComputedStyle(inputRef.current).maxHeight, 15);

            if (scrollHeight > maxHeight) {
                inputRef.current.style.height = `${maxHeight}px`;
            } else {
                inputRef.current.style.height = `${scrollHeight}px`;
            }
        }
    };

    useEffect(() => {
        adjustHeight();
    }, [input]);

    return (
        <>
         <div className={styles.inputBarContainer}>
            {/* <div className={styles.inputBar}> */}
                {/* Image Preview Section */}

                {/* Input Field Section */}
                <div className={styles.inputWrapper}>
                    <div className={styles.inputBoxContainer}>
                        <textarea
                            ref={inputRef}
                            placeholder="Type your message"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={async(e) => {
                                if (e.key === 'Enter' && !e.shiftKey) {
                                    e.preventDefault();
                                    await handleSend();
                                }
                            }}
                            // onPaste={handlePaste}
                            className={styles.inputField}
                            rows={1}
                        />
                    </div>

                    {/* Icons Section */}
                    <div className={styles.iconBoxContainer}>
                        <div className={styles.iconBoxLeftContainer}>
                         <Tooltip title="Upload Folder" placement="left">
                            <label htmlFor="fileUpload" className={styles.webSearchContainer}>
                                <input
                                    type="file"
                                    webkitdirectory="" 
                                    directory=""
                                    id="fileUpload"
                                    onChange={handleFilePathChange}
                                    className={styles.hiddenInput}
                                />

                                <FaFolderPlus className={`${styles.scanIcon} ${styles.icons}`} />
                                {/* <span>Upload</span> */}
                              </label>
                              </Tooltip>

                             {folderName && ( <label htmlFor="fileUpload" className={styles.webSearchContainer}>  
                               <FcOpenedFolder className={`${styles.scanIcon} ${styles.icons}`} />
                                <span>{folderName}</span> 
                              </label>)}
                             
                        </div>
                        <div className={styles.iconBoxRightContainer}>
                        </div>
                    </div>
                </div>
         </div>
        </>
    );
};

export default InputBar;
