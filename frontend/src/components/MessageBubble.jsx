export default function MessageBubble({
  role,
  content
}) {

  const isUser =
    role==="user";

  return (

    <div className={`
      flex mb-3
      ${
        isUser
        ?
        "justify-end"
        :
        "justify-start"
      }
    `}>

      <div className={`
        px-4
        py-2
        rounded-lg
        shadow
        max-w-xl
        ${
          isUser
          ?
          "bg-blue-600 text-white"
          :
          "bg-white"
        }
      `}>

        {content}

      </div>

    </div>
  );
}