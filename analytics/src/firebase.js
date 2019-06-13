import firebase from "firebase/app";
import "firebase/firestore";

firebase.initializeApp({
  apiKey: "AIzaSyCT-9SIQICMO14zbYNsQ-pm5Tkj3WOP7Fg",
  // authDomain: "### FIREBASE AUTH DOMAIN ###",
  projectId: "anconia-4008c"
});

export const db = firebase.firestore();
