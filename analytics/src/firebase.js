import firebase from "firebase/app";
import "firebase/firestore";

firebase.initializeApp({
  apiKey: "AIzaSyCiuEW53FG7l34-usnKz4aNW7C850OVj9I",
  // authDomain: "### FIREBASE AUTH DOMAIN ###",
  projectId: "anconia-project"
});

export const db = firebase.firestore();
