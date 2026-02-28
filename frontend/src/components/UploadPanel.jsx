export default function UploadPanel() {

  const upload = async (file) => {

    const form =
      new FormData();

    form.append(
      "file",
      file
    );

    await fetch(
      "http://127.0.0.1:8000/admin/upload",
      {
        method: "POST",
        body: form,
      }
    );

    alert(
      "Upload complete"
    );
  };

  return (

    <input
      type="file"
      className="mb-4"
      onChange={(e) =>
        upload(
          e.target.files[0]
        )
      }
    />

  );
}