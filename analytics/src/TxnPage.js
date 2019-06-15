import React, { Component } from "react";
import { db } from "./firebase";
import { Graph } from "react-d3-graph";

// the graph configuration, you only need to pass down properties
// that you want to override, otherwise default ones will be used
const myConfig = {
  directed: false,
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
        nodes: [{ id: "Genesis" }],
        links: []
      }
    };
  }

  async componentDidMount() {
    const query = db
      .collection("transactions")
      .orderBy("created_at", "desc")
      .limit(1);

    const querySnapshot = await query.get();
    const docId = querySnapshot.docs[0].id;

    db.collection("transactions")
      .doc(docId)
      .collection("transactions")
      .onSnapshot(snapshot => {
        const docs = snapshot.docs;

        const nodes = docs.map(doc => ({
          id: doc.id
        }));

        let links = [];

        docs.forEach(doc => {
          const txn = doc.data();
          if (txn.children.length) {
            txn.children.forEach(child => {
              links.push({
                source: doc.id,
                target: child
              });
            });
          }
        });

        const newData = { nodes, links };
        this.setState({ data: newData });

        // const nodes = peers.map(peer => ({
        //   id: peer
        // }));
        // const links = peers.map(peer => ({
        //   source: SOURCE_NODE,
        //   target: peer
        // }));

        // let newData = Object.assign({}, this.state.data);
        // newData.nodes = [{ id: SOURCE_NODE }].concat(nodes);
        // newData.links = [].concat(links);

        // this.setState({ data: newData });
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
