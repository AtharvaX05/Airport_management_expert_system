document.addEventListener('DOMContentLoaded', () => {
  const flights = [
    { id:1, name:'Flight A', destination:'New York' },
    { id:2, name:'Flight B', destination:'London' },
    { id:3, name:'Flight C', destination:'Dubai' }
  ];

  const flightSelect = document.getElementById('flight');
  const flightList = document.getElementById('flight-list');

  flights.forEach(f => {
    flightSelect.innerHTML += `<option value="${f.id}">${f.name} - ${f.destination}</option>`;
    flightList.innerHTML += `<div class="card"><h3>${f.name}</h3><p>Destination: ${f.destination}</p></div>`;
  });

  // Booking form
  const form = document.getElementById('booking-form');
  form.addEventListener('submit', e => {
    e.preventDefault();
    const passengerName = document.getElementById('passenger-name').value;
    const flightId = document.getElementById('flight').value;

    fetch('http://localhost:5000/book', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ passengerName, flightId })
    })
    .then(res => res.json())
    .then(data => {
      alert(data.message);
      form.reset();
    })
    .catch(err => alert("Error booking flight: " + err));
  });

  // Chatbot toggle
  const chatbotToggle = document.getElementById('chatbot-toggle');
  const chatbot = document.getElementById('chatbot');
  chatbotToggle.addEventListener('click', () => {
    chatbot.style.display = (chatbot.style.display==='flex')?'none':'flex';
  });

  // Chatbot messaging
  const chatMessages = document.getElementById('chatbot-messages');
  const chatInput = document.getElementById('chatbot-text');
  const chatSend = document.getElementById('chatbot-send');

  function appendMessage(sender,text){
    const div = document.createElement('div');
    div.textContent = `${sender}: ${text}`;
    div.style.alignSelf = sender==='Bot'?'flex-start':'flex-end';
    div.style.background = sender==='Bot'?'#2c3e50':'#3498db';
    div.style.color='white'; div.style.padding='5px 10px'; div.style.borderRadius='10px';
    div.style.margin='5px 0'; div.style.maxWidth='80%';
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function sendMessage(){
    const message = chatInput.value.trim();
    if(!message) return;
    appendMessage('You',message); chatInput.value='';
    fetch('http://localhost:5000/chat',{
      method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({message})
    })
    .then(res=>res.json())
    .then(data=>appendMessage('Bot',data.reply))
    .catch(err=>appendMessage('Bot','Error: server not reachable'));
  }

  chatSend.addEventListener('click',sendMessage);
  chatInput.addEventListener('keypress',e=>{if(e.key==='Enter') sendMessage();});
});
