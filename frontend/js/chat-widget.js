const chatbot = document.querySelector("[data-chatbot]");

if (chatbot) {
  const launcher = chatbot.querySelector("[data-chatbot-open]");
  const windowPanel = chatbot.querySelector("[data-chatbot-window]");
  const closeButton = chatbot.querySelector("[data-chatbot-close]");
  const form = chatbot.querySelector("[data-chatbot-form]");
  const messages = chatbot.querySelector("[data-chatbot-messages]");
  const choices = chatbot.querySelector("[data-chatbot-choices]");
  const inputSlot = chatbot.querySelector("[data-chatbot-input-slot]");
  const inputLabel = chatbot.querySelector("[data-chatbot-input-label]");
  const submit = chatbot.querySelector("[data-chatbot-submit]");
  const status = chatbot.querySelector("[data-chatbot-status]");
  const questions = [
    { key: "subject", prompt: "How can Mani best support your team or project today?", options: ["A full-time role", "A project opportunity", "A collaboration"] },
    { key: "name", prompt: "May I know your name?", autocomplete: "name" },
    { key: "email", prompt: "What is the best email address for a reply?", type: "email", autocomplete: "email" },
    { key: "message", prompt: "Please share any details you would like Mani to know.", multiline: true },
  ];
  let answers = {};
  let index = 0;

  function closeConversation() {
    chatbot.classList.remove("is-open");
    windowPanel.hidden = true;
    launcher.hidden = false;
  }

  function revealAfterAbout() {
    const about = document.querySelector("#about");
    if (!about) {
      chatbot.classList.add("is-visible");
      return;
    }

    const reveal = () => {
      if (window.scrollY + window.innerHeight < about.offsetTop + about.offsetHeight) return;
      chatbot.classList.add("is-visible");
      window.removeEventListener("scroll", reveal);
    };

    reveal();
    window.addEventListener("scroll", reveal, { passive: true });
  }

  function setStatus(message = "", isError = false) {
    status.textContent = message;
    status.classList.toggle("is-error", isError);
  }

  function addMessage(text, author = "assistant") {
    const bubble = document.createElement("p");
    bubble.className = `chatbot-widget__message chatbot-widget__message--${author}`;
    bubble.textContent = text;
    messages.appendChild(bubble);
    messages.scrollTop = messages.scrollHeight;
  }

  async function portfolioReply(intent) {
    try {
      const response = await fetch("/api/assistant/reply/", {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify({ intent }),
      });
      const data = await response.json();
      return response.ok ? data.reply : "Thank you for considering Mani. Please share a few details so he can respond thoughtfully.";
    } catch (_error) {
      return "Thank you for considering Mani. Please share a few details so he can respond thoughtfully.";
    }
  }

  async function submitAnswer(value) {
    const question = questions[index];
    if (!value) return;
    choices.innerHTML = "";
    inputSlot.innerHTML = "";
    answers[question.key] = value;
    addMessage(value, "visitor");
    index += 1;
    if (question.key === "subject") addMessage(await portfolioReply(value));
    showQuestion();
  }

  function showQuestion() {
    choices.innerHTML = "";
    inputSlot.innerHTML = "";
    const question = questions[index];

    if (!question) {
      sendMessage();
      return;
    }

    addMessage(question.prompt);
    if (question.options) {
      question.options.forEach((option) => {
        const button = document.createElement("button");
        button.type = "button";
        button.textContent = option;
        button.addEventListener("click", () => submitAnswer(option));
        choices.appendChild(button);
      });
      return;
    }

    const field = document.createElement(question.multiline ? "textarea" : "input");
    field.className = "chatbot-widget__input";
    field.name = question.key;
    field.required = true;
    field.placeholder = "Type your answer";
    field.autocomplete = question.autocomplete || "off";
    if (!question.multiline) field.type = question.type || "text";
    if (question.multiline) field.rows = 3;
    inputLabel.textContent = question.prompt;
    inputSlot.appendChild(field);
    submit.hidden = false;
    submit.textContent = index === questions.length - 1 ? "Send" : "Next";
    field.focus();
  }

  function startConversation() {
    answers = {};
    index = 0;
    messages.innerHTML = "";
    choices.innerHTML = "";
    inputSlot.innerHTML = "";
    submit.hidden = true;
    setStatus();
    chatbot.classList.add("is-open");
    launcher.hidden = true;
    windowPanel.hidden = false;
    addMessage("Welcome. I am Mani's portfolio assistant, and I would be glad to help you connect.");
    window.setTimeout(showQuestion, 220);
  }

  async function sendMessage() {
    submit.hidden = true;
    setStatus("Sending...");
    try {
      const response = await fetch("/api/contact/submit/", {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify(answers),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Message could not be sent.");
      setStatus();
      addMessage("Thank you. Mani will get back to you soon.");
      window.setTimeout(closeConversation, 1800);
    } catch (error) {
      setStatus(error.message || "Message failed. Please email Mani directly.", true);
    }
  }

  launcher.addEventListener("click", startConversation);
  closeButton.addEventListener("click", closeConversation);

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const field = inputSlot.querySelector("input, textarea");
    const value = field?.value.trim() || "";
    if (!value) return field?.focus();
    if (field.type === "email" && !field.checkValidity()) return field.focus();
    submitAnswer(value);
  });

  revealAfterAbout();
}
