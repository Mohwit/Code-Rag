import styles from './CanvasNavbar.module.css';
import ThemeToggle from '../ThemeToggle/ThemeToggle'
import { Space, Switch, Tooltip, Popconfirm } from 'antd';
import { CheckCircleOutlined, CloseCircleOutlined } from "@ant-design/icons";
import { MdOutlineClose } from "react-icons/md";

const CanvasNavbar = ({ handleAccept, handleReject, setOpenCanvas, setSplitView, splitView, canvasState ,theme,setTheme}) => {
 
    const isToggleDisabled = !canvasState?.oldFile || !canvasState?.newFile;

    const status = canvasState?.verified
        ? canvasState?.accepted
            ? { label: "Accepted", color: "#28a745", icon: <CheckCircleOutlined /> }
            : { label: "Rejected", color: "#dc3545", icon: <CloseCircleOutlined /> }
        : { label: "Pending", color: "#A9A9A9", icon: null };

    return (
        <>
            {/* Close Canvas */}
            <Tooltip title="Close Canvas">
                <MdOutlineClose 
                    className={styles.crossIcon} 
                    onClick={() => setOpenCanvas(false)} 
                />
            </Tooltip>

            <div className={styles.menuItems}>
                {/* Status Indicator */}
                <div className={styles.statusIndicator} style={{ color: status.color }}>
                    {status.icon} <span>{status.label}</span>
                </div>

                {/* Accept/Reject Buttons */}
                <div className={styles.decisionMenuItem}>
                    <Tooltip title={canvasState?.needsVerification && !canvasState?.verified ? "Accept Changes" : "Disabled"}>
                        <CheckCircleOutlined 
                            onClick={canvasState?.needsVerification && !canvasState?.verified ? handleAccept : null}
                            style={{
                                fontSize: "1.3rem",
                                color: canvasState?.needsVerification && !canvasState?.verified ? "#28a745" : "#A9A9A9", 
                                cursor: canvasState?.needsVerification && !canvasState?.verified ? "pointer" : "not-allowed",
                                opacity: canvasState?.needsVerification && !canvasState?.verified ? 1 : 0.5
                            }}
                        />
                    </Tooltip>

                    {/* Reject Button with Confirmation */}
                    <Popconfirm
                        title="Are you sure you want to reject the changes?"
                        onConfirm={handleReject}
                        okText="Yes, Reject"
                        cancelText="Cancel"
                        disabled={!(canvasState?.needsVerification && !canvasState?.verified)}
                    >
                        <Tooltip title={canvasState?.needsVerification && !canvasState?.verified ? "Reject Changes" : "Disabled"}>
                            <CloseCircleOutlined 
                                style={{
                                    fontSize: "1.3rem",
                                    color: canvasState?.needsVerification && !canvasState?.verified ? "#dc3545" : "#A9A9A9",
                                    cursor: canvasState?.needsVerification && !canvasState?.verified ? "pointer" : "not-allowed",
                                    opacity: canvasState?.needsVerification && !canvasState?.verified ? 1 : 0.5
                                }}
                            />
                        </Tooltip>
                    </Popconfirm>
                </div>

                {/* Toggle Diff View */}
                <Tooltip title={isToggleDisabled ? "No Diff Available" : "Toggle Diff View"}>
                    <Space direction="vertical">
                        <Switch 
                            checkedChildren="Split"
                            unCheckedChildren="Inline" 
                            checked={splitView}
                            disabled={isToggleDisabled} 
                            onChange={() => setSplitView(!splitView)}
                            style={{
                                backgroundColor: isToggleDisabled ? "#A9A9A9" : (splitView ? "#28a745" : "#FF8C00"),
                                cursor: isToggleDisabled ? "not-allowed" : "pointer",
                                opacity: isToggleDisabled ? 0.5 : 1
                            }}
                        />
                    </Space>
                </Tooltip>

             {/* Toggle Theme */}
             <Tooltip title="Theme">
               <ThemeToggle setTheme={setTheme} theme={theme}/>
             </Tooltip>

            </div>
        </>
    );
};

export default CanvasNavbar;
