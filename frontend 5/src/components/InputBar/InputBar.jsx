// InputBar.jsx with Ant Design enhancements
import React, { useEffect, useRef, useState } from 'react';
import styles from './InputBar.module.css';
import { FaFolderPlus, FaPlus, FaTimes, FaFile, FaSearch, FaFileAlt, FaFileCode, FaFileImage, FaFilePdf } from "react-icons/fa";
import { Tooltip, Modal, Input, Empty, List, Avatar, Tag, Button, Typography } from 'antd';
import { FcOpenedFolder } from "react-icons/fc";
import { FileOutlined, SearchOutlined, SendOutlined, UploadOutlined } from '@ant-design/icons';

const { Text } = Typography;

// Helper to determine file icon based on extension
const getFileIcon = (fileName) => {
    const extension = fileName.split('.').pop().toLowerCase();
    
    if (['jpg', 'jpeg', 'png', 'gif', 'svg', 'webp'].includes(extension)) {
        return <FaFileImage style={{ color: '#36cfc9' }} />;
    } else if (['pdf'].includes(extension)) {
        return <FaFilePdf style={{ color: '#f5222d' }} />;
    } else if (['js', 'jsx', 'ts', 'tsx', 'html', 'css', 'py', 'java', 'c', 'cpp', 'go', 'rb'].includes(extension)) {
        return <FaFileCode style={{ color: '#722ed1' }} />;
    } else if (['txt', 'md', 'json', 'csv', 'xml'].includes(extension)) {
        return <FaFileAlt style={{ color: '#faad14' }} />;
    }
    
    return <FaFile style={{ color: '#1890ff' }} />;
};

const InputBar = ({ 
    input, 
    setInput, 
    handleSend, 
    isLoading, 
    folderStructure, 
    selectedFiles = [],
    setSelectedFiles
}) => {
    const inputRef = useRef(null);
    const [filePath, setFilePath] = useState(""); 
    const [folderName, setFolderName] = useState("");
    const [isMentionActive, setIsMentionActive] = useState(false);
    const [mentionQuery, setMentionQuery] = useState('');
    const [fileModalVisible, setFileModalVisible] = useState(false);
    const [searchQuery, setSearchQuery] = useState('');
    const [cursorPosition, setCursorPosition] = useState(0);
    const mentionListRef = useRef(null);
    
    // Function to get all files from folder structure recursively
    const getAllFiles = (items = folderStructure) => {
        if (!items || !Array.isArray(items)) return [];
        
        let files = [];
        items.forEach(item => {
            if (item.type === 'file') {
                files.push(item);
            } else if (item.type === 'folder' && item.children) {
                files = [...files, ...getAllFiles(item.children)];
            }
        });
        return files;
    };
    
    const allFiles = getAllFiles();
    
    // Function to filter files based on search query
    const getFilteredFiles = (query = '') => {
        if (!query.trim()) return allFiles;
        const lowerQuery = query.toLowerCase();
        return allFiles.filter(file => 
            file.name.toLowerCase().includes(lowerQuery) || 
            file.path.toLowerCase().includes(lowerQuery)
        );
    };
    
    // Filter files based on mention query
    const filteredFilesForMention = mentionQuery 
        ? getFilteredFiles(mentionQuery)
        : allFiles;
    
    // Filter files for the modal
    const filteredFilesForModal = getFilteredFiles(searchQuery);

    
    const handleFileSelection = (file) => {
        // Check if file is already selected
        if (!selectedFiles.some(f => f.path === file.path)) {
            setSelectedFiles([...selectedFiles, file]);
        }
        setFileModalVisible(false);
    };
    
    const handleRemoveFile = (filePath) => {
        setSelectedFiles(selectedFiles.filter(file => file.path !== filePath));
    };
    
    const handleMentionSelection = (file) => {
        // Replace the @query with the selected file mention
        const beforeCursor = input.substring(0, cursorPosition).replace(/@[^@\s]*$/, `@${file.path} `);
        const afterCursor = input.substring(cursorPosition);
        
        const newInput = beforeCursor + afterCursor;
        setInput(newInput);
        setIsMentionActive(false);
        setMentionQuery('');
        
        // Add the file to selected files if not already there
        if (!selectedFiles.some(f => f.path === file.path)) {
            setSelectedFiles([...selectedFiles, file]);
        }
        
        // Set focus back to input after a brief delay
        setTimeout(() => {
            inputRef.current.focus();
            const newCursorPos = beforeCursor.length;
            inputRef.current.selectionStart = newCursorPos;
            inputRef.current.selectionEnd = newCursorPos;
        }, 0);
    };
    
    // Handle input changes
    const handleInputChange = (e) => {
        const value = e.target.value;
        setInput(value);
        
        // Set cursor position
        setCursorPosition(e.target.selectionStart);
        
        // Check for @ symbol
        const cursorPos = e.target.selectionStart;
        const textBeforeCursor = value.substring(0, cursorPos);
        const mentionMatch = textBeforeCursor.match(/@([^@\s]*)$/);
        
        if (mentionMatch) {
            setIsMentionActive(true);
            setMentionQuery(mentionMatch[1]);
        } else {
            setIsMentionActive(false);
        }
    };
    
    // Handle key navigation in mention list
    const handleKeyDown = async (e) => {
        if (e.key === 'Enter' && !e.shiftKey && !isMentionActive) {
            e.preventDefault();
            await handleSend();
        } else if (isMentionActive) {
            if (e.key === 'Escape' || e.key === 'Tab') {
                e.preventDefault();
                setIsMentionActive(false);
            } else if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
                e.preventDefault();
                
                // Navigation logic for mention list
                if (mentionListRef.current) {
                    const items = mentionListRef.current.querySelectorAll(`.${styles.mentionItem}`);
                    if (items.length === 0) return;
                    
                    const activeItem = mentionListRef.current.querySelector(`.${styles.activeItem}`);
                    let nextIndex = 0;
                    
                    if (activeItem) {
                        const currentIndex = Array.from(items).indexOf(activeItem);
                        if (e.key === 'ArrowDown') {
                            nextIndex = (currentIndex + 1) % items.length;
                        } else {
                            nextIndex = (currentIndex - 1 + items.length) % items.length;
                        }
                    }
                    
                    // Remove active class from all items
                    items.forEach(item => item.classList.remove(styles.activeItem));
                    // Add active class to the next item
                    items[nextIndex].classList.add(styles.activeItem);
                    items[nextIndex].scrollIntoView({ block: 'nearest' });
                }
            } else if (e.key === 'Enter') {
                e.preventDefault();
                
                // Select the currently active item
                if (mentionListRef.current) {
                    const activeItem = mentionListRef.current.querySelector(`.${styles.activeItem}`);
                    if (activeItem) {
                        const filePath = activeItem.getAttribute('data-path');
                        const file = allFiles.find(f => f.path === filePath);
                        if (file) {
                            handleMentionSelection(file);
                        }
                    } else if (filteredFilesForMention.length > 0) {
                        // If no active item but we have filtered files, select the first one
                        handleMentionSelection(filteredFilesForMention[0]);
                    }
                }
            }
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
    
    // Use effect to set first item as active when mention list changes
    useEffect(() => {
        if (isMentionActive && mentionListRef.current) {
            const items = mentionListRef.current.querySelectorAll(`.${styles.mentionItem}`);
            if (items.length > 0) {
                // Remove active class from all items
                items.forEach(item => item.classList.remove(styles.activeItem));
                // Add active class to the first item
                items[0].classList.add(styles.activeItem);
            }
        }
    }, [isMentionActive, mentionQuery, filteredFilesForMention]);

    return (
        <>
            <div className={styles.inputBarContainer}>
                {/* Selected Files Preview Section */}
                {selectedFiles.length > 0 && (
                    <div className={styles.selectedFilesContainer}>
                        {selectedFiles.map((file, index) => (
                            <Tag
                                key={index}
                                className={styles.selectedFileTag}
                                closable
                                onClose={() => handleRemoveFile(file.path)}
                                icon={getFileIcon(file.name)}
                                color="blue"
                            >
                                {file.name}
                            </Tag>
                        ))}
                    </div>
                )}
                
                {/* Input Field Section */}
                <div className={styles.inputWrapper}>
                    <div className={styles.inputBoxContainer}>
                        <textarea
                            ref={inputRef}
                            placeholder="Type your message or use @ to reference files"
                            value={input}
                            onChange={handleInputChange}
                            onKeyDown={handleKeyDown}
                            className={styles.inputField}
                            rows={1}
                        />
                        
                        {/* Mention dropdown */}
                        {isMentionActive && (
                            <div className={styles.mentionDropdown} ref={mentionListRef}>
                                <div className={styles.mentionHeader}>
                                    <SearchOutlined className={styles.mentionSearchIcon} />
                                    <span>Referencing files...</span>
                                </div>
                                <div className={styles.mentionList}>
                                    {filteredFilesForMention.length > 0 ? (
                                        <List
                                            itemLayout="horizontal"
                                            dataSource={filteredFilesForMention.slice(0, 10)}
                                            renderItem={(file, index) => (
                                                <List.Item
                                                    className={`${styles.mentionItem} ${index === 0 ? styles.activeItem : ''}`}
                                                    onClick={() => handleMentionSelection(file)}
                                                    data-path={file.path}
                                                >
                                                    <List.Item.Meta
                                                        className={styles.listItemMeta}
                                                        avatar={<Avatar icon={getFileIcon(file.name)}  />}
                                                        title={file.name}
                                                        description={<Text type="secondary" ellipsis>{file.path}</Text>}
                                                    />
                                                </List.Item>
                                            )}
                                        />
                                    ) : (
                                        <div className={styles.noMentionMatches}>
                                            <Empty
                                                image={Empty.PRESENTED_IMAGE_SIMPLE}
                                                description="No matching files found"
                                            />
                                        </div>
                                    )}
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Icons Section */}
                    <div className={styles.iconBoxContainer}>
                        <div className={styles.iconBoxLeftContainer}>
                            
                            <Tooltip title="Select Files" placement="top">
                                <Button
                                    type="text"
                                    icon={<FileOutlined />}
                                    className={styles.iconButton}
                                    onClick={() => {
                                        setFileModalVisible(true);
                                        setSearchQuery('');
                                    }}
                                />
                            </Tooltip>
                        </div>
                        <div className={styles.iconBoxRightContainer}>
                            <Button
                                type="primary"
                                icon={<SendOutlined />}
                                onClick={handleSend}
                                disabled={isLoading || !input.trim()}
                                className={styles.sendButton}
                            />
                        </div>
                    </div>
                </div>
            </div>
            
            {/* File Selection Modal */}
            <Modal
                title={
                    <div className={styles.modalHeader}>
                        <FileOutlined style={{ marginRight: 8 }} />
                        Select Files
                    </div>
                }
                open={fileModalVisible}
                onCancel={() => setFileModalVisible(false)}
                footer={null}
                width={600}
                className={styles.fileSelectionModal}
            >
                <div className={styles.fileModalSearch}>
                    <Input
                        prefix={<SearchOutlined />}
                        placeholder="Search for files..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className={styles.fileSearchInput}
                        allowClear
                    />
                </div>
                
                <div className={styles.fileModalList}>
                    {allFiles.length > 0 ? (
                        filteredFilesForModal.length > 0 ? (
                            <List
                                itemLayout="horizontal"
                                dataSource={filteredFilesForModal}
                                renderItem={(file) => (
                                    <List.Item
                                        className={styles.fileModalListItem}
                                        onClick={() => handleFileSelection(file)}
                                        actions={[
                                            <Button 
                                                size="small" 
                                                type="primary"
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    handleFileSelection(file);
                                                }}
                                            >
                                                Select
                                            </Button>
                                        ]}
                                    >
                                        <List.Item.Meta
                                            avatar={<Avatar icon={getFileIcon(file.name)} />}
                                            title={file.name}
                                            description={
                                                <Text type="secondary" ellipsis>
                                                    {file.path}
                                                </Text>
                                            }
                                        />
                                    </List.Item>
                                )}
                            />
                        ) : (
                            <Empty 
                                description="No files found matching your search" 
                                image={Empty.PRESENTED_IMAGE_SIMPLE}
                            />
                        )
                    ) : (
                        <Empty 
                            description="No files available. Please upload a folder first." 
                            image={Empty.PRESENTED_IMAGE_SIMPLE}
                        />
                    )}
                </div>
            </Modal>
        </>
    );
};

export default InputBar;