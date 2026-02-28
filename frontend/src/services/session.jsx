export const getSession = () => {

  let id = localStorage.getItem(
    "sessionId"
  );

  if (!id) {

    id = crypto.randomUUID();

    localStorage.setItem(
      "sessionId",
      id
    );
  }

  return id;
};

export const newSession = () => {

  const id = crypto.randomUUID();

  localStorage.setItem(
    "sessionId",
    id
  );

  return id;
};