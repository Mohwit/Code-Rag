import DiffViewer from "react-diff-viewer";
import ReactDiffViewer, { DiffMethod } from 'react-diff-viewer';

const DiffViewerComponent = ({canvasState , splitView , theme}) => {
  return (
    <>
      <ReactDiffViewer 
         oldValue={canvasState?.oldFile} 
          newValue={canvasState?.newFile} 
          splitView={splitView}
          compareMethod={DiffMethod.WORDS}
          useDarkTheme={theme === 'dark' ? true : false}
           />
          
    </>
  );
}

export default DiffViewerComponent;
