document.addEventListener('DOMContentLoaded', () => {

    // --- Helper function to add message to chat display ---
    function addMessageToChat(sender, message, container, emotion = null, isPlaceholder = false) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('chat-message', sender);
        if (isPlaceholder) {
            messageDiv.classList.add('placeholder'); // Add a class for easy selection
        }

        const nameStrong = document.createElement('strong');
        nameStrong.textContent = (sender === 'user' ? 'You:' : 'Therabot:');

        const messageP = document.createElement('p');
        messageP.textContent = message;

        const innerP = document.createElement('p');
        innerP.appendChild(nameStrong);

        // Only add emotion tag if it's NOT a placeholder and emotion is relevant
        if (sender === 'bot' && !isPlaceholder && emotion && emotion !== 'neutral' && emotion !== 'error') {
            const emotionSpan = document.createElement('span');
            emotionSpan.classList.add('emotion-tag');

            // Add emoji based on emotion type
            let emoji = '';
            switch (emotion.toLowerCase()) {
                case 'happy':
                    emoji = '😊';
                    break;
                case 'sad':
                    emoji = '😢';
                    break;
                case 'angry':
                    emoji = '😡';
                    break;
                case 'surprised':
                    emoji = '😲';
                    break;
                case 'worried':
                    emoji = '😟';
                    break;
                case 'neutral':
                    emoji = '😐';
                    break;
                default:
                    emoji = '🤔'; // Default if emotion is not recognized
            }

            emotionSpan.textContent = ` ${emoji} (${emotion})`; // Include emoji with emotion
            innerP.appendChild(emotionSpan);
        }

        messageDiv.appendChild(innerP);
        messageDiv.appendChild(messageP);

        container.appendChild(messageDiv);
        scrollToBottom(container);
        return messageDiv; // Return the created element
    }

    // --- Helper function to scroll chat history ---
    function scrollToBottom(container) {
        if (container) {
            setTimeout(() => {
                container.scrollTop = container.scrollHeight;
            }, 0);
        }
    }

    // --- FAQ Accordion ---
    const faqItems = document.querySelectorAll('.faq-item');
    faqItems.forEach(item => {
        const question = item.querySelector('.faq-question');
        if (question) {
            question.addEventListener('click', () => {
                item.classList.toggle('active');
            });
        }
    });

    // --- Auto-scroll Chat (Initial Load) ---
    const chatHistoryContainer = document.getElementById('chat-history');
    if (chatHistoryContainer) {
        scrollToBottom(chatHistoryContainer);
    }

    // --- Add 'active' class to current nav link ---
    const navLinks = document.querySelectorAll('header nav a');
    const currentPath = window.location.pathname;

    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            if (!link.classList.contains('active')) {
                link.classList.add('active');
            }
        }
    });

    // --- Theme Toggle ---
    const themeToggle = document.getElementById('theme-toggle');
    const body = document.body;
    const currentTheme = localStorage.getItem('theme');

    if (currentTheme === 'dark') {
        body.classList.add('dark-mode');
        if (themeToggle) {
            themeToggle.innerHTML = '☀️';
            themeToggle.title = "Switch to light mode";
        }
    } else {
        if (themeToggle) {
            themeToggle.innerHTML = '🌙';
            themeToggle.title = "Switch to dark mode";
        }
    }

    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            body.classList.toggle('dark-mode');
            if (body.classList.contains('dark-mode')) {
                localStorage.setItem('theme', 'dark');
                themeToggle.innerHTML = '☀️';
                themeToggle.title = "Switch to light mode";
            } else {
                localStorage.setItem('theme', 'light');
                themeToggle.innerHTML = '🌙';
                themeToggle.title = "Switch to dark mode";
            }
        });
    }

    // --- AJAX Chat Form Submission ---
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const rainAudio = document.getElementById('rain-audio'); // Get audio element
    const rainToggleButton = document.getElementById('rain-toggle-button'); // Get toggle button
    const audioControls = document.getElementById('audio-controls'); // Get audio controls container
    const volumeSlider = document.getElementById('volume-slider'); // Get volume slider

    // --- Rain Audio Functions ---
    function playRainSound() {
        if (rainAudio && audioControls) {
            // Set initial volume from slider if available
            if (volumeSlider) {
                rainAudio.volume = volumeSlider.value;
            }
            
            // Add better error handling with user feedback
            rainAudio.play().catch(e => {
                console.error("Error playing audio:", e);
                // Show an error message to the user
                const chatHistoryContainer = document.getElementById('chat-history');
                if (chatHistoryContainer) {
                    addMessageToChat('bot', "Sorry, I couldn't play the rain sounds. Please check that your browser allows audio playback.", chatHistoryContainer, 'error');
                }
            });
            
            audioControls.style.display = 'flex'; // Show the audio controls container
        } else {
            // Handle missing audio element or controls
            console.error("Rain audio element or controls not found");
            const chatHistoryContainer = document.getElementById('chat-history');
            if (chatHistoryContainer) {
                addMessageToChat('bot', "Sorry, I couldn't play the rain sounds. Audio player not initialized properly.", chatHistoryContainer, 'error');
            }
        }
    }

    function stopRainSound() {
        if (rainAudio) {
            rainAudio.pause();
            rainAudio.currentTime = 0; // Reset audio to start
            if (audioControls) {
                audioControls.style.display = 'none'; // Hide the audio controls container
            }
        }
    }

    function toggleRainSound() {
        if (rainAudio) {
            if (rainAudio.paused) {
                playRainSound();
            } else {
                stopRainSound();
            }
        }
    }

    // Add listener for the rain toggle button
    if (rainToggleButton) {
        rainToggleButton.addEventListener('click', toggleRainSound);
    }

    // Add listener for the volume slider
    if (volumeSlider && rainAudio) {
        // Set initial audio volume based on slider's default value
        rainAudio.volume = volumeSlider.value;

        volumeSlider.addEventListener('input', () => {
            if (rainAudio) {
                rainAudio.volume = volumeSlider.value;
            }
        });
    }

    if (chatForm && chatInput && chatHistoryContainer) {
        chatForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            const userMessage = chatInput.value.trim();
            if (!userMessage) {
                return;
            }

            // --- Check for "stop music" command ---
            if (userMessage.toLowerCase().includes('stop music') || 
                userMessage.toLowerCase().includes('stop rain') ||
                userMessage.toLowerCase().includes('turn off music') ||
                userMessage.toLowerCase().includes('turn off rain')) {
                stopRainSound();
                // Add user message for feedback
                addMessageToChat('user', userMessage, chatHistoryContainer);
                // Add bot acknowledgment
                addMessageToChat('bot', "I've turned off the rain sounds.", chatHistoryContainer);
                chatInput.value = ''; // Clear input
                chatInput.focus();
                return; // Stop processing this message further
            }

            // Add user message
            addMessageToChat('user', userMessage, chatHistoryContainer);
            chatInput.value = '';
            chatInput.focus();

            // Check if we have a selected mood from the modal
            const selectedMood = localStorage.getItem('current_chat_mood');

            // Create data object for AJAX
            const requestData = {
                message: userMessage
            };

            // Add mood if available
            if (selectedMood) {
                requestData.mood = selectedMood;
                // Clear the mood after first message (it's per session)
                localStorage.removeItem('current_chat_mood');
            }

            // Add placeholder for bot response
            let placeholderMessageElement = addMessageToChat('bot', '...', chatHistoryContainer, null, true);

            try {
                const response = await fetch(chatForm.action, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },
                    body: JSON.stringify(requestData)
                });

                // Find the placeholder to update/remove it
                const placeholder = chatHistoryContainer.querySelector('.chat-message.bot.placeholder');

                if (!response.ok) {
                    let errorMsg = `Error: ${response.status} ${response.statusText}`;
                    try {
                        const errorData = await response.json();
                        errorMsg = errorData.error || errorMsg;
                    } catch (e) { }
                    console.error('Fetch Error:', errorMsg);
                    if (placeholder) {
                        // Update placeholder with error
                        placeholder.querySelector('p:last-child').textContent = `Sorry, couldn't get a response. ${errorMsg}`;
                        placeholder.classList.remove('placeholder'); // Remove placeholder status
                    } else {
                        // Fallback if placeholder somehow missing
                        addMessageToChat('bot', `Sorry, couldn't get a response. ${errorMsg}`, chatHistoryContainer, 'error');
                    }
                    return;
                }

                const responseData = await response.json();

                if (placeholder) {
                    placeholder.classList.remove('placeholder'); // Remove placeholder status
                    if (responseData.error) {
                        console.error('App Error:', responseData.error);
                        placeholder.querySelector('p:last-child').textContent = responseData.error;
                    } else if (responseData.warning) {
                        console.warn('App Warning:', responseData.warning);
                        placeholder.querySelector('p:last-child').textContent = responseData.warning;
                    } else if (responseData.bot_reply) {
                        // Update placeholder content with the actual reply
                        // Replace newlines from backend with <br> for HTML display
                        placeholder.querySelector('p:last-child').innerHTML = responseData.bot_reply.replace(/\n/g, '<br>');

                        // Add emotion tag if present
                        if (responseData.emotion && responseData.emotion !== 'neutral') {
                            const emotionSpan = document.createElement('span');
                            emotionSpan.classList.add('emotion-tag');
                            emotionSpan.textContent = ` (${responseData.emotion})`;
                            // Ensure the strong tag exists before appending
                            const strongTag = placeholder.querySelector('p:first-child strong');
                            if (strongTag) {
                                strongTag.parentNode.appendChild(emotionSpan);
                            }
                        }

                        // --- Rain Audio Control ---
                        if (responseData.play_rain) {
                            playRainSound();
                        }
                        // --------------------------

                        if (responseData.action === 'end_chat') {
                            chatInput.disabled = true;
                            chatInput.placeholder = "Chat ended. Refresh to start again.";
                            stopRainSound(); // Stop rain sound if chat ends
                        }
                    }
                } else {
                    // Fallback if placeholder is missing
                    if (responseData.error) addMessageToChat('bot', responseData.error, chatHistoryContainer, 'error');
                    else if (responseData.warning) addMessageToChat('bot', responseData.warning, chatHistoryContainer, 'warning');
                    else if (responseData.bot_reply) {
                        addMessageToChat('bot', responseData.bot_reply.replace(/\n/g, '<br>'), chatHistoryContainer, responseData.emotion);
                        // --- Rain Audio Control (Fallback) ---
                        if (responseData.play_rain) {
                            playRainSound();
                        }
                        // --------------------------
                    }
                }

                // Scroll after adding/updating message
                scrollToBottom(chatHistoryContainer);

            } catch (error) {
                console.error('Network/Fetch Error:', error);
                // Update or add error message in placeholder or new message
                const placeholder = chatHistoryContainer.querySelector('.chat-message.bot.placeholder');
                
                // Get more specific error message
                let errorMessage = 'Sorry, there was a network problem. Please check your connection and try again.';
                if (error.name === 'AbortError') {
                    errorMessage = 'The request timed out. Please try again.';
                } else if (error.message && error.message.includes('Failed to fetch')) {
                    // Try to reconnect in background
                    setTimeout(() => {
                        fetch('/chat', {method: 'HEAD'})
                            .then(() => console.log('Background connection check: Success'))
                            .catch(() => console.error('Background connection check: Failed'));
                    }, 5000);
                }
                
                if (placeholder) {
                    placeholder.querySelector('p:last-child').textContent = errorMessage;
                    placeholder.classList.remove('placeholder');
                } else {
                    addMessageToChat('bot', errorMessage, chatHistoryContainer, 'error');
                }
                
                scrollToBottom(chatHistoryContainer); // Scroll after error message
            }
        });
    }

    // --- Voice Input Setup (if browser supports it) ---
    const micButton = document.createElement('button');
    micButton.type = 'button';
    micButton.innerHTML = '🎤';
    micButton.title = 'Use voice input';
    micButton.style.cssText = 'background: none; border: none; font-size: 1.5rem; cursor: pointer; padding: 0 10px;';

    // Check if browser supports speech recognition
    if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
        if (chatForm) chatForm.insertBefore(micButton, chatForm.querySelector('button[type="submit"]'));

        // Voice Recognition
        micButton.addEventListener('click', () => {
            const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.lang = 'en'; // Default to English
            recognition.start();

            recognition.onresult = (event) => {
                const spokenText = event.results[0][0].transcript;
                document.getElementById('chat-input').value = spokenText;
            };

            recognition.onerror = (event) => {
                console.error('Voice recognition error:', event.error);
            };
        });
    }

    // --- MOOD SELECTION MODAL ---
    const moodModal = document.getElementById('mood-modal');
    const closeMoodModal = document.querySelector('.close-modal');
    const skipMoodBtn = document.getElementById('skip-mood');
    const confirmMoodBtn = document.getElementById('confirm-mood');
    const moodOptions = document.querySelectorAll('.mood-option');
    let selectedMood = null;
    
    // Check if this is the chat page
    if (moodModal) {
        // Use the flag from the server to determine whether to show the modal
        // This ensures it only shows after a fresh login/session start
        if (window.showMoodModalOnLoad === true) {
            setTimeout(() => {
                moodModal.style.display = 'block';
            }, 500);
        }
    }
    
    // Modal close button
    if (closeMoodModal) {
        closeMoodModal.addEventListener('click', () => {
            moodModal.style.display = 'none';
        });
    }

    // Skip mood selection
    if (skipMoodBtn) {
        skipMoodBtn.addEventListener('click', () => {
            moodModal.style.display = 'none';
        });
    }

    // Select a mood
    if (moodOptions) {
        moodOptions.forEach(option => {
            option.addEventListener('click', () => {
                // Remove selected class from all options
                moodOptions.forEach(opt => opt.classList.remove('selected'));
                // Add selected class to clicked option
                option.classList.add('selected');
                selectedMood = option.dataset.mood;
            });
        });
    }

    // Function to send the initial greeting with the selected mood
    function sendInitialGreeting(mood) {
        // Only send if we have a chat history container and chatForm
        const chatHistory = document.getElementById('chat-history');
        if (!chatHistory || !chatForm) return;
        
        // Check if there are already messages in the chat
        const existingMessages = chatHistory.querySelectorAll('.chat-message');
        
        // If there are messages, we should just update the emotion on the first bot message
        if (existingMessages.length > 0) {
            // Find the first bot message
            const firstBotMessage = Array.from(existingMessages).find(msg => msg.classList.contains('bot'));
            
            if (firstBotMessage && mood) {
                // Get emoji for the mood
                let moodEmoji = '';
                switch (mood) {
                    case 'happy': moodEmoji = '😊'; break;
                    case 'angry': moodEmoji = '😡'; break;
                    case 'sad': moodEmoji = '😞'; break;
                    case 'worried': moodEmoji = '😟'; break;
                    case 'neutral': moodEmoji = '😐'; break;
                }
                
                // Find or create an emotion tag
                let emotionTag = firstBotMessage.querySelector('.emotion-tag');
                const strongTag = firstBotMessage.querySelector('p:first-child strong');
                
                if (!emotionTag && strongTag) {
                    // Create a new emotion tag
                    emotionTag = document.createElement('span');
                    emotionTag.classList.add('emotion-tag');
                    strongTag.parentNode.appendChild(emotionTag);
                }
                
                if (emotionTag) {
                    emotionTag.textContent = ` ${moodEmoji} (${mood})`;
                }
                
                // Now send a hidden message to update the chatbot's context
                // with the selected mood, but don't show it in the chat
                fetch(chatForm.action, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },
                    body: JSON.stringify({
                        message: "I'm feeling " + mood,
                        mood: mood,
                        hidden: true
                    })
                }).then(response => response.json())
                  .then(data => {
                      // Update the bot's first message with content that matches the mood
                      if (data.bot_reply) {
                          firstBotMessage.querySelector('p:last-child').innerHTML = data.bot_reply.replace(/\n/g, '<br>');
                      }
                  })
                  .catch(error => {
                      console.error('Error updating mood context:', error);
                  });
            }
            return;
        }
        
        // If no messages exist yet, proceed as normal
        // The server will handle creating the initial greeting with the correct mood
    }

    // Confirm mood selection
    if (confirmMoodBtn) {
        confirmMoodBtn.addEventListener('click', () => {
            if (selectedMood) {
                // Store the selected mood for the session
                localStorage.setItem('current_chat_mood', selectedMood);
                
                // Close the modal
                moodModal.style.display = 'none';
                
                // Send initial greeting with the mood
                sendInitialGreeting(selectedMood);
                
                // Get emoji for the mood to update any existing messages
                let moodEmoji = '';
                switch (selectedMood) {
                    case 'happy': moodEmoji = '😊'; break;
                    case 'angry': moodEmoji = '😡'; break;
                    case 'sad': moodEmoji = '😞'; break;
                    case 'worried': moodEmoji = '😟'; break;
                    case 'neutral': moodEmoji = '😐'; break;
                }
                
                // Update any existing bot messages to add the mood
                const chatHistory = document.getElementById('chat-history');
                if (chatHistory) {
                    const botMessages = chatHistory.querySelectorAll('.chat-message.bot');
                    if (botMessages.length > 0) {
                        const firstBotMessage = botMessages[0]; // Get the first bot message
                        const strongTag = firstBotMessage.querySelector('p:first-child strong');
                        
                        // Check if there's already an emotion tag
                        let emotionTag = firstBotMessage.querySelector('.emotion-tag');
                        
                        if (!emotionTag && strongTag) {
                            // Create a new emotion tag
                            emotionTag = document.createElement('span');
                            emotionTag.classList.add('emotion-tag');
                            strongTag.parentNode.appendChild(emotionTag);
                        }
                        
                        if (emotionTag) {
                            emotionTag.textContent = ` ${moodEmoji} (${selectedMood})`;
                        }
                    }
                }
            } else {
                moodModal.style.display = 'none';
            }
        });
    }

    // Close modal if user clicks outside of it
    window.addEventListener('click', (event) => {
        if (event.target === moodModal) {
            moodModal.style.display = 'none';
        }
    });

    // --- JOURNAL FUNCTIONALITY ---
    // Check if we're on the journal page
    const journalPage = document.querySelector('.journal-container');
    if (journalPage) {
        // Calendar variables
        let currentDate = new Date();
        let currentMonth = currentDate.getMonth();
        let currentYear = currentDate.getFullYear();
        let selectedDate = null;
        let journalEntries = [];
        let currentEntry = null;
        let selectedMoodForJournal = null;

        // Get DOM elements
        const calendarDaysContainer = document.getElementById('calendar-days');
        const calendarMonthYear = document.getElementById('calendar-month-year');
        const prevMonthBtn = document.getElementById('prev-month');
        const nextMonthBtn = document.getElementById('next-month');
        const entriesList = document.getElementById('entries-list');
        const journalDateDisplay = document.getElementById('journal-date');
        const journalContent = document.getElementById('journal-content');
        const saveEntryBtn = document.getElementById('save-entry');
        const deleteEntryBtn = document.getElementById('delete-entry');
        const editorMessage = document.getElementById('editor-message');
        const moodButtons = document.querySelectorAll('.mood-btn');

        // Format date as YYYY-MM-DD (for API calls)
        function formatDateForAPI(date) {
            return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
        }

        // Format date for display (Month DD, YYYY)
        function formatDateForDisplay(dateString) {
            const date = new Date(dateString);
            return date.toLocaleDateString('en-US', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
        }

        // Load and display journal entries
        function loadJournalEntries() {
            fetch('/journal/entries')
                .then(response => response.json())
                .then(data => {
                    journalEntries = data;
                    renderEntriesList();
                    renderCalendar();
                })
                .catch(error => {
                    console.error('Error loading journal entries:', error);
                    entriesList.innerHTML = '<div class="no-entries">Could not load entries. Please try again.</div>';
                });
        }

        // Render the list of entries
        function renderEntriesList() {
            if (journalEntries.length === 0) {
                entriesList.innerHTML = '<div class="no-entries">No entries yet. Select a date to create your first entry.</div>';
                return;
            }

            let entriesHTML = '';
            journalEntries.forEach(entry => {
                // Get emoji for mood
                let moodEmoji = '';
                if (entry.mood) {
                    switch (entry.mood) {
                        case 'happy': moodEmoji = '😊'; break;
                        case 'angry': moodEmoji = '😡'; break;
                        case 'sad': moodEmoji = '😞'; break;
                        case 'worried': moodEmoji = '😟'; break;
                        case 'neutral': moodEmoji = '😐'; break;
                        default: moodEmoji = '';
                    }
                }

                const displayDate = new Date(entry.date).toLocaleDateString('en-US', {
                    month: 'short',
                    day: 'numeric'
                });

                entriesHTML += `
                    <div class="entry-item" data-date="${entry.date}">
                        <div class="entry-header">
                            <span class="entry-date">${displayDate}</span>
                            <span class="entry-mood">${moodEmoji}</span>
                        </div>
                        <div class="entry-preview">${entry.preview}</div>
                    </div>
                `;
            });

            entriesList.innerHTML = entriesHTML;

            // Add click events to entries
            document.querySelectorAll('.entry-item').forEach(item => {
                item.addEventListener('click', function () {
                    const date = this.dataset.date;
                    selectDate(new Date(date));
                });
            });
        }

        // Render the calendar
        function renderCalendar() {
            // Update month and year display
            const monthNames = ['January', 'February', 'March', 'April', 'May', 'June',
                'July', 'August', 'September', 'October', 'November', 'December'];
            calendarMonthYear.textContent = `${monthNames[currentMonth]} ${currentYear}`;

            // Get first day of the month
            const firstDay = new Date(currentYear, currentMonth, 1).getDay();

            // Get number of days in the month
            const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();

            // Clear previous calendar days
            calendarDaysContainer.innerHTML = '';

            // Add empty cells for days before the first day of the month
            for (let i = 0; i < firstDay; i++) {
                const dayElement = document.createElement('div');
                dayElement.classList.add('calendar-day', 'empty');
                calendarDaysContainer.appendChild(dayElement);
            }

            // Get today's date for highlighting
            const today = new Date();
            const isCurrentMonth = (today.getMonth() === currentMonth && today.getFullYear() === currentYear);
            const todayDate = today.getDate();

            // Add days of the month
            for (let day = 1; day <= daysInMonth; day++) {
                const dayElement = document.createElement('div');
                dayElement.classList.add('calendar-day');
                dayElement.textContent = day;

                // Add data attribute for the date
                const dateStr = `${currentYear}-${String(currentMonth + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
                dayElement.dataset.date = dateStr;

                // Check if this day is today
                if (isCurrentMonth && day === todayDate) {
                    dayElement.classList.add('today');
                }

                // Check if this day is selected
                if (selectedDate &&
                    day === selectedDate.getDate() &&
                    currentMonth === selectedDate.getMonth() &&
                    currentYear === selectedDate.getFullYear()) {
                    dayElement.classList.add('selected');
                }

                // Check if this day has an entry
                const hasEntry = journalEntries.some(entry => entry.date === dateStr);
                if (hasEntry) {
                    dayElement.classList.add('has-entry');

                    // Find the entry to get its mood
                    const entry = journalEntries.find(e => e.date === dateStr);
                    if (entry && entry.mood) {
                        // Add mood marker
                        const moodMarker = document.createElement('span');
                        moodMarker.classList.add('mood-marker');

                        // Choose emoji based on mood
                        switch (entry.mood) {
                            case 'happy': moodMarker.textContent = '😊'; break;
                            case 'angry': moodMarker.textContent = '😡'; break;
                            case 'sad': moodMarker.textContent = '😞'; break;
                            case 'worried': moodMarker.textContent = '😟'; break;
                            case 'neutral': moodMarker.textContent = '😐'; break;
                        }

                        dayElement.appendChild(moodMarker);
                    }
                }

                // Add click event
                dayElement.addEventListener('click', function () {
                    // Get the date from the data attribute
                    const clickedDate = new Date(this.dataset.date);
                    selectDate(clickedDate);
                });

                calendarDaysContainer.appendChild(dayElement);
            }
        }

        // Handle date selection
        function selectDate(date) {
            // Update selected date
            selectedDate = date;
            const dateStr = formatDateForAPI(date);

            // Update calendar display
            document.querySelectorAll('.calendar-day').forEach(day => {
                if (day.dataset.date === dateStr) {
                    day.classList.add('selected');
                } else {
                    day.classList.remove('selected');
                }
            });

            // Update journal date display
            journalDateDisplay.textContent = formatDateForDisplay(dateStr);

            // Load entry for the selected date
            loadEntry(dateStr);
        }

        // Load an entry for a specific date
        function loadEntry(dateStr) {
            // Show loading state
            journalContent.disabled = true;
            journalContent.value = 'Loading...';
            saveEntryBtn.disabled = true;
            deleteEntryBtn.disabled = true;

            // Reset mood buttons
            moodButtons.forEach(btn => btn.classList.remove('active'));
            selectedMoodForJournal = null;

            // Fetch the entry from the API
            fetch(`/journal/entry/${dateStr}`)
                .then(response => response.json())
                .then(data => {
                    currentEntry = data;

                    // Populate the editor
                    journalContent.value = data.content;
                    journalContent.disabled = false;
                    saveEntryBtn.disabled = false;

                    // Only enable delete button if this is an existing entry
                    deleteEntryBtn.disabled = data.is_new;

                    // Set the mood if available
                    if (data.mood) {
                        selectedMoodForJournal = data.mood;
                        const moodBtn = document.querySelector(`.mood-btn[data-mood="${data.mood}"]`);
                        if (moodBtn) {
                            moodBtn.classList.add('active');
                        }
                    }
                })
                .catch(error => {
                    console.error('Error loading entry:', error);
                    journalContent.value = 'Could not load entry. Please try again.';
                });
        }

        // Save the current entry
        function saveEntry() {
            if (!selectedDate) return;

            const dateStr = formatDateForAPI(selectedDate);
            const content = journalContent.value.trim();

            if (!content) {
                showEditorMessage('Please enter some content before saving.', 'error');
                return;
            }

            // Disable buttons during save
            saveEntryBtn.disabled = true;
            deleteEntryBtn.disabled = true;

            // Prepare data for API
            const entryData = {
                content: content,
                mood: selectedMoodForJournal
            };

            // Send to API
            fetch(`/journal/entry/${dateStr}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(entryData)
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showEditorMessage(data.message, 'success');

                        // Refresh entries to update the list
                        loadJournalEntries();

                        // Enable delete button as we now have an entry
                        deleteEntryBtn.disabled = false;
                    } else {
                        showEditorMessage(data.error || 'Error saving entry', 'error');
                    }
                })
                .catch(error => {
                    console.error('Error saving entry:', error);
                    showEditorMessage('Could not save entry. Please try again.', 'error');
                })
                .finally(() => {
                    saveEntryBtn.disabled = false;
                });
        }

        // Delete the current entry
        function deleteEntry() {
            if (!selectedDate || !currentEntry || currentEntry.is_new) return;

            if (!confirm('Are you sure you want to delete this entry? This cannot be undone.')) {
                return;
            }

            const dateStr = formatDateForAPI(selectedDate);

            // Disable buttons during delete
            saveEntryBtn.disabled = true;
            deleteEntryBtn.disabled = true;

            // Send delete request to API
            fetch(`/journal/entry/${dateStr}`, {
                method: 'DELETE'
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showEditorMessage(data.message, 'success');

                        // Clear the editor
                        journalContent.value = '';

                        // Reset mood buttons
                        moodButtons.forEach(btn => btn.classList.remove('active'));
                        selectedMoodForJournal = null;

                        // Refresh entries to update the list
                        loadJournalEntries();

                        // Disable delete button as the entry is now gone
                        deleteEntryBtn.disabled = true;
                    } else {
                        showEditorMessage(data.error || 'Error deleting entry', 'error');
                        deleteEntryBtn.disabled = false;
                    }
                })
                .catch(error => {
                    console.error('Error deleting entry:', error);
                    showEditorMessage('Could not delete entry. Please try again.', 'error');
                    deleteEntryBtn.disabled = false;
                })
                .finally(() => {
                    saveEntryBtn.disabled = false;
                });
        }

        // Show a message in the editor
        function showEditorMessage(message, type) {
            editorMessage.textContent = message;
            editorMessage.className = 'editor-message ' + type;
            editorMessage.style.display = 'block';

            // Hide after a delay
            setTimeout(() => {
                editorMessage.style.display = 'none';
            }, 3000);
        }

        // Event Listeners
        if (prevMonthBtn) {
            prevMonthBtn.addEventListener('click', () => {
                currentMonth--;
                if (currentMonth < 0) {
                    currentMonth = 11;
                    currentYear--;
                }
                renderCalendar();
            });
        }

        if (nextMonthBtn) {
            nextMonthBtn.addEventListener('click', () => {
                currentMonth++;
                if (currentMonth > 11) {
                    currentMonth = 0;
                    currentYear++;
                }
                renderCalendar();
            });
        }

        if (saveEntryBtn) {
            saveEntryBtn.addEventListener('click', saveEntry);
        }

        if (deleteEntryBtn) {
            deleteEntryBtn.addEventListener('click', deleteEntry);
        }

        if (moodButtons) {
            moodButtons.forEach(btn => {
                btn.addEventListener('click', function () {
                    // Remove active class from all mood buttons
                    moodButtons.forEach(b => b.classList.remove('active'));

                    // Add active class to clicked button
                    this.classList.add('active');

                    // Store the selected mood
                    selectedMoodForJournal = this.dataset.mood;
                });
            });
        }

        // Initial setup
        loadJournalEntries();
        renderCalendar();

        // Auto-select today's date
        selectDate(new Date());
    }

}); // End DOMContentLoaded
