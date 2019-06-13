import React, { Component } from "react";
import { db } from "./firebase";
import { Graph } from "react-d3-graph";

// the graph configuration, you only need to pass down properties
// that you want to override, otherwise default ones will be used
const myConfig = {
  height: 300,
  width: 700,
  nodeHighlightBehavior: true,
  node: {
    color: "lightgreen",
    size: 500,
    highlightStrokeColor: "blue"
  },
  link: {
    highlightColor: "lightblue"
  }
};

const SOURCE_NODE = "Current node";

export default class NodesPage extends Component {
  constructor(props) {
    super(props);
    this.state = {
      data: {
        nodes: [{ id: SOURCE_NODE }],
        links: []
      }
    };
  }

  async componentDidMount() {
    const query = db
      .collection("nodes")
      .orderBy("created_at", "desc")
      .limit(1);

    const querySnapshot = await query.get();
    const docId = querySnapshot.docs[0].id;

    db.collection("nodes")
      .doc(docId)
      .onSnapshot(doc => {
        const data = doc.data();
        const peers = data.peers;

        const nodes = peers.map(peer => ({
          id: peer
        }));
        const links = peers.map(peer => ({
          source: SOURCE_NODE,
          target: peer
        }));

        let newData = Object.assign({}, this.state.data);
        newData.nodes = [{ id: SOURCE_NODE }].concat(nodes);
        newData.links = [].concat(links);

        this.setState({ data: newData });
      });
  }

  render() {
    const { data } = this.state;

    return (
      <div className="graph-container">
        <Graph id="graph-id" data={data} config={myConfig} />
        <div>Number of peers: {data.nodes.length - 1}</div>
      </div>
    );
  }
}
