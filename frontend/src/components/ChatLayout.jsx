import { useState } from "react";
import Sidebar from "./Sidebar";
import ChatWindow from "./ChatWindow";
import {
  getSession
} from "../services/session";

export default function ChatLayout() {

  const [
    sessionId,
    setSessionId
  ] = useState(getSession());

  return (

    <div className="flex h-screen">

      <Sidebar
        sessionId={sessionId}
        setSessionId={setSessionId}
      />

      <ChatWindow
        sessionId={sessionId}
      />

    </div>

  );
}