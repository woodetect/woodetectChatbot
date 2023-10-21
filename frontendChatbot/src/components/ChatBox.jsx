import { useState, useEffect } from 'react'
import '@chatscope/chat-ui-kit-styles/dist/default/styles.min.css'
import { ChatBubbleBottomCenterIcon } from "@heroicons/react/24/outline";
import { MainContainer,
         ChatContainer,
         MessageList,
         Message,
         MessageInput,
         ConversationHeader,
         ConversationList,
         Conversation,
         TypingIndicator
        } from '@chatscope/chat-ui-kit-react'

export default function ChatBox() {
  const [typing, setTyping] = useState(false);
  const [hidden, setHidden] = useState(true);
  const [messages, setMessages] = useState([
    {
      message: "Bonjour, je suis le chatbot de Woodetect. Comment puis-je vous aider ?",
      sender: "bot"
    }
  ])

  //const m = React.useMemo(() => messages, [messages]);

  const handleSend = async (message) => {
    const newMessageUser = {
      message: message,
      sender: "user",
      direction: "outgoing"
    }
    const newMessageBot = {
      message: "thinking...",
      sender: "bot",
      direction: "incoming"
    }
    const newMessages = [...messages, newMessageUser, newMessageBot];
    setMessages(newMessages);
    setTyping(true);
    await processMessageToChat(newMessageUser)
  }

  async function processMessageToChat(newMessage) {
    const request_url = "http://127.0.0.1:5000/send_message";

    console.log("Sending message to backend :", newMessage);
    const data = {
      message: newMessage.message,
    };
    fetch(request_url, {
      method: 'POST',
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data) 
    })
    .then(response => response.json()) // Parse the response as JSON
    .then(data => {
        setTyping(true);
    })
    .catch(error => {
        console.error('Error:', error);
    });
  }

  function updateLastElement(array, newValue) {
    if (Array.isArray(array) && array.length > 1) {
      return array.map((item, index) => {
        if (index === array.length - 1 && item.sender === "bot") {
          return newValue;
        } else {
          return item;
        }
      });
    } else {
      // Handle the case where the input array is empty or not an array
      return array;
    }
  }

  useEffect(() => {
   console.log("Messages :", messages);
  }, [messages]);  
    // Poll for updates from the backend server
    useEffect(() => {
      let waiting = false;
      const interval = setInterval(async () => {
        /*try {
          await fetch('http://127.0.0.1:5000/check_waiting', {
            method: "GET",
          })
          .then(response => response.json())
          .then(data => {
            console.log("Waiting for user to send message :", data.reply)
            waiting = data.reply === 'False' ? false : true; 
          })
        } catch (error) {
          console.error('Failed to fetch data:', error);
          return;
        }
        if (waiting === true) {
          console.log("still waiting...")
          return;
        }*/
        try {
          await fetch('http://127.0.0.1:5000/get_last_sentence')
          .then(response => response.json())
          .then(data => {
            if (data.reply === '' || data.reply === null) {
              return;
            }
            console.log("Bot message  :", data.reply);
            setMessages(prevMessages => updateLastElement(prevMessages, { message: data.reply,
                                                                          sender: "bot", direction: "incoming" }));
          })
        } catch (error) {
          return;
        }
      }, 1000); // TODO change to 500
  
      return () => clearInterval(interval);
    }, [messages]);

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
