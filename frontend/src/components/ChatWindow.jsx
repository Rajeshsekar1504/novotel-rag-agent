import { useState } from "react";
import MessageBubble from "./MessageBubble";
import SourcePanel from "./SourcePanel";
import { streamMessage } from "../services/api";

export default function ChatWindow({ sessionId }) {

  const [messages, setMessages] = useState([]);
  const [sources, setSources] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {

    if (!input.trim()) return;

    const userMsg = {
      role: "user",
      content: input,
    };

    setMessages(prev => [...prev, userMsg]);

    setInput("");

    let botContent = "";

    const botMsg = {
      role: "assistant",
      content: "",
    };

    setMessages(prev => [...prev, botMsg]);

    setLoading(true);

    await streamMessage(

      sessionId,

      userMsg.content,

      (token) => {

        botContent += token;

        setMessages(prev => {

          const copy = [...prev];

          copy[copy.length - 1].content = botContent;

          return copy;
        });

      },

      (sources) => {

        setSources(sources);

        setLoading(false);

      },

      (error) => {

        console.error(error);

        setLoading(false);

      }

    );

  };

  return (

    <div className="flex flex-col flex-1">

      <div className="bg-blue-700 text-white p-4 font-bold">
        NovaTel Assistant
      </div>

      <div className="flex-1 overflow-y-auto p-4 bg-gray-100">

        {messages.map((m, i) => (
          <MessageBubble key={i} {...m} />
        ))}

        {loading && (
          <div>Typing...</div>
        )}

        <SourcePanel sources={sources} />

      </div>

      <div className="p-4 border-t flex gap-2">

        <input
          value={input}
          onChange={(e) =>
            setInput(e.target.value)
          }
          onKeyDown={(e) => {
            if (e.key === "Enter")
              handleSend();
          }}
          className="flex-1 border p-2 rounded"
        />

        <button
          onClick={handleSend}
          className="bg-blue-600 text-white px-4 rounded"
        >
          Send
        </button>

      </div>

    </div>

  );
}