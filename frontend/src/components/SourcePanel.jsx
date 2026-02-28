export default function SourcePanel({
  sources
}) {

  if (!sources.length)
    return null;

  return (

    <div className="
      bg-white
      p-3
      mt-3
      rounded
      shadow
    ">

      <div className="
        font-bold
        mb-2
      ">
        Sources
      </div>

      {sources.map(
        (s,i)=>(

          <div key={i}>
            {s.source}
          </div>

      ))}

    </div>
  );
}