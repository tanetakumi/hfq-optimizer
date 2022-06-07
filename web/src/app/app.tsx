import React from 'react';
import ReactDOM from 'react-dom';

const App: React.FC<{ compiler: string, framework: string , test: string}> = (props) => {
  return (
    <div>
      <div>{props.compiler}</div>
      <div>{props.framework}</div>
      <div>{props.test}</div>
      <div>こんにちわ</div>
    </div>
  );
}

ReactDOM.render(
  <App compiler="TypeScript" framework="React" test="Youtube"/>,
  document.getElementById("test")
);