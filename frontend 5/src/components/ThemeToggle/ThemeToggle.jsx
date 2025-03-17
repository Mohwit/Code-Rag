import React from "react";
import { Segmented } from "antd";
import { SunOutlined, MoonOutlined } from "@ant-design/icons";
import styles from "./ThemeToggle.module.css";

const ThemeToggle = ({ theme, setTheme }) => {
  return (
    <Segmented
      options={[
        {
          label: <SunOutlined />,
          value: "light",
        },
        {
          label: <MoonOutlined />,
          value: "dark",
        },
      ]}
      value={theme} 
      onChange={(value) => setTheme(value)}
      className={styles.themeToggle}
    />
  );
};

export default ThemeToggle;
