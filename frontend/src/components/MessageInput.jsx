import { useEffect, useRef } from "react";

export default function MessageInput({
  input,
  setInput,
  sendMessage,
  isLoading = false,
  isConnected = true,
}) {
  const inputRef = useRef(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();

      if (!isLoading && isConnected) {
        sendMessage();
      }
    }
  };

  const handleSubmit = () => {
    if (
      !input.trim() ||
      isLoading ||
      !isConnected
    ) {
      return;
    }

    sendMessage();
  };

  const disabled =
    isLoading || !isConnected;

  return (
    <div className="message-input">

      <input
        ref={inputRef}
        type="text"
        value={input}
        disabled={disabled}
        placeholder={
          isLoading
            ? "AI is analyzing the emails..."
            : isConnected
              ? "Ask the AI about Enron emails..."
              : "Connecting to AI..."
        }
        onChange={(event) =>
          setInput(event.target.value)
        }
        onKeyDown={handleKeyDown}
        autoComplete="off"
      />

      <button
        type="button"
        onClick={handleSubmit}
        disabled={
          disabled || !input.trim()
        }
        aria-label="Send message"
        title={
          isLoading
            ? "AI is processing..."
            : "Send message"
        }
      >

        {isLoading ? (
          <span className="loading-dots">
            <span></span>
            <span></span>
            <span></span>
          </span>
        ) : (
          "📩"
        )}

      </button>

    </div>
  );
}