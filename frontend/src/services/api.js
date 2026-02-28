import axios from "axios";

const BASE_URL = "http://127.0.0.1:8000";

export const sendMessage = async (
  sessionId,
  message
) => {

  const res = await axios.post(
    BASE_URL + "/chat",
    {
      session_id: sessionId,
      message: message,
    }
  );

  return res.data;
};


export const streamMessage = async (
  sessionId,
  message,
  onToken,
  onDone,
  onError
) => {

  try {

    const response = await fetch(
      BASE_URL + "/chat/stream",
      {
        method: "POST",
        headers: {
          "Content-Type":
            "application/json",
        },
        body: JSON.stringify({
          session_id: sessionId,
          message: message,
        }),
      }
    );

    if (!response.body)
      throw new Error("No body");

    const reader =
      response.body.getReader();

    const decoder =
      new TextDecoder();

    let buffer = "";

    while (true) {

      const {
        done,
        value
      } = await reader.read();

      if (done) break;

      buffer += decoder.decode(value);

      const lines =
        buffer.split("\n");

      buffer = lines.pop();

      for (const line of lines) {

        if (!line.trim())
          continue;

        const data =
          JSON.parse(line);

        if (data.token)
          onToken(data.token);

        if (data.done)
          onDone(data.sources);

        if (data.error)
          onError(data.error);
      }
    }

  } catch (err) {

    console.error(err);

    onError(err.message);

  }
};