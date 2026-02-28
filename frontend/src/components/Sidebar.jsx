import {
  newSession
} from "../services/session";
import UploadPanel from "./UploadPanel";

export default function Sidebar({
  sessionId,
  setSessionId
}) {

  const createNew = () => {

    const id = newSession();

    setSessionId(id);
  };

  return (

    <div className="
      w-64
      bg-gray-900
      text-white
      p-4
      flex
      flex-col
    ">

      <div className="
        font-bold
        text-lg
        mb-4
      ">
        NovaTel AI
      </div>

      <button
        onClick={createNew}
        className="
          bg-blue-600
          p-2
          rounded
          mb-4
        "
      >
        + New Chat
      </button>

      <UploadPanel />

      <div className="
        mt-auto
        text-xs
        text-gray-400
      ">
        Session:
        <br />
        {sessionId}
      </div>

    </div>

  );
}