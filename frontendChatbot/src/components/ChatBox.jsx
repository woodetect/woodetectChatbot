import { useState } from 'react'
import '@chatscope/chat-ui-kit-styles/dist/default/styles.min.css'
import { ChatBubbleBottomCenterIcon } from "@heroicons/react/24/outline";
import { MainContainer, ChatContainer, MessageList, Message, MessageInput, ConversationHeader, ConversationList, Conversation, TypingIndicator } from '@chatscope/chat-ui-kit-react'

export default function ChatBox() {
  const [typing, setTyping] = useState(false);
  const [hidden, setHidden] = useState(true);
  const [messages, setMessages] = useState([
    {
      message: "Bonjour, je suis le chatbot de Woodetect. Comment puis-je vous aider ?",
      sender: "bot"
    }
  ])

  const handleSend = async (message) => {
    const newMessage = {
      message: message,
      sender: "user",
      direction: "outgoing"
    }
    const newMessages = [...messages, newMessage];
    setMessages(newMessages);
    setTyping(true);
    await processMessageToChat(newMessage)
  }

  async function processMessageToChat(newMessage) {
    const request_url = "http://127.0.0.1:80/send_message";

    await fetch(request_url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(newMessage)
    })
    .then(response => response.json()) // Parse the response as JSON
    .then(data => {
        console.log(data.reply); // Access the 'reply' field in the data object
        let stackedMessages = [newMessage, { message: data.reply, sender: "bot", direction: "incoming" }]
        setMessages([...messages, ...stackedMessages]);
        setTyping(false);
    })
    .catch(error => {
        console.error('Error:', error);
    });
  }

  const darkGreen = 'rgb(41, 92, 60, 0.6)';
  const lightGreen = 'rgb(105, 163, 142, 0.7)';
  const white = 'rgb(250, 240, 230, 0.7)';
  const typingElement = (
    <p style={{ color: 'black', backgroundColor: white }}>
      Woodetect is typing...
    </p>
  );
  return (
      <div
        style={{
          position: 'fixed',
          bottom: '20px', // Adjust as needed
          right: '20px', // Adjust as needed
          zIndex: '9999', // Ensure it's above other elements
        }}
        >
        {!hidden && <ChatContainer style={{
          backgroundColor: lightGreen, // Green background color
          padding: '10px', // Adjust as needed for spacing
          borderRadius: '15px', // Rounded border
          position: 'relative',
          bottom: '60px',
          right: '60px',
          width: '400px',
        }}>
          <MessageList style={{
            borderRadius: '15px', // Rounded border
            backgroundColor: darkGreen,
          }}
            typingIndicator={typing ? typingElement : null}
          >
            {messages.map((message, index) => {
              const messageStyle = {
                borderRadius: '25px', // Rounded border
                padding: '5px', // Adjust as needed for spacing
              };
              return <Message key={index} model={message} style={messageStyle}/>
            })}
          </MessageList>
          <MessageInput style={{
            borderRadius: '15px', // Rounded border
            backgroundColor: darkGreen,
          }}
           placeholder="Type message here" onSend={handleSend}/>
        </ChatContainer>}
        <button onClick={() => setHidden(!hidden)} style={{
          borderRadius: '50%', // Makes the button round
          width: '50px', // Adjust the size as needed
          height: '50px', // Adjust the size as needed
          backgroundColor: darkGreen, // Example background color
          justifyContent: 'center',
          alignItems: 'center',
          cursor: 'pointer',
          position: 'absolute',
          bottom: '15px',
          right: '15px',
        }}>
          <ChatBubbleBottomCenterIcon style={{
            width: '1.5rem',
            height: '1.5rem',
            position: 'relative',
            left: '-6px',
            top: '3px',
          
          }}/>
        </button>
      </div>
  )
}
