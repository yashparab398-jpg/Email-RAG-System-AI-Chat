const questions = [
  "Legal risk emails",
  "Kenneth Lay communications",
  "Energy trading discussions",
  
];

export default function SuggestedQuestions({
  setInput,
}) {
  return (
    <div className="suggestions">
      {questions.map((question) => (
        <button
          key={question}
          className="question-button"
          onClick={() =>
            setInput(question)
          }
        >
          {question}
        </button>
      ))}
    </div>
  );
}