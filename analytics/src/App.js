import React, { Component } from "react";
import "./App.css";
import NodesPage from "./NodesPage";
import TxnPage from "./TxnPage";

class App extends Component {
  render() {
    return (
      <div className="App">
        {/* <NodesPage /> */}
        <TxnPage />
      </div>
    );
  }
}

export default App;
