import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";

const firebaseConfig = {
  apiKey: "***REMOVED***",
  authDomain: "the-cube-7885.firebaseapp.com",
  projectId: "the-cube-7885",
  storageBucket: "the-cube-7885.firebasestorage.app",
  messagingSenderId: "492034233693",
  appId: "1:492034233693:web:83daaf2dfe83de6030c4b4"
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);