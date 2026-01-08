// AI Voice Assistant for Wallet Engine
// Uses Web Speech API for voice recognition and text-to-speech

class VoiceAssistant {
    constructor() {
        this.recognition = null;
        this.synthesis = window.speechSynthesis;
        this.isListening = false;
        this.conversationHistory = [];
        this.initSpeechRecognition();
    }

    initSpeechRecognition() {
        // Check for browser support
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

        if (!SpeechRecognition) {
            console.error('Speech Recognition not supported in this browser');
            this.showError('Voice recognition is not supported in your browser. Please use Chrome or Edge.');
            return;
        }

        this.recognition = new SpeechRecognition();
        this.recognition.continuous = false;
        this.recognition.interimResults = false;
        this.recognition.lang = 'en-US';

        this.recognition.onstart = () => {
            this.isListening = true;
            this.updateUIState('listening');
        };

        this.recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            this.handleVoiceCommand(transcript);
        };

        this.recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            this.isListening = false;
            this.updateUIState('idle');
            if (event.error !== 'no-speech') {
                this.showError(`Voice recognition error: ${event.error}`);
            }
        };

        this.recognition.onend = () => {
            this.isListening = false;
            this.updateUIState('idle');
        };
    }

    startListening() {
        if (!this.recognition) {
            this.showError('Voice recognition not initialized');
            return;
        }

        if (this.isListening) {
            this.recognition.stop();
            return;
        }

        try {
            this.recognition.start();
            this.addToConversation('system', 'Listening...');
        } catch (error) {
            console.error('Error starting recognition:', error);
            this.showError('Failed to start voice recognition');
        }
    }

    async handleVoiceCommand(command) {
        this.addToConversation('user', command);
        this.updateUIState('processing');

        try {
            const result = await this.processCommand(command);
            this.addToConversation('assistant', result.message);
            this.speak(result.message);
        } catch (error) {
            const errorMsg = `Sorry, I encountered an error: ${error.message}`;
            this.addToConversation('assistant', errorMsg);
            this.speak(errorMsg);
        }

        this.updateUIState('idle');
    }

    async processCommand(command) {
        const lowerCommand = command.toLowerCase();

        // Create User
        if (lowerCommand.includes('create user') || lowerCommand.includes('add user')) {
            return await this.createUser(command);
        }

        // List Users
        if (lowerCommand.includes('show users') || lowerCommand.includes('list users') || lowerCommand.includes('get users')) {
            return await this.listUsers();
        }

        // Create Wallet
        if (lowerCommand.includes('create wallet') || lowerCommand.includes('add wallet')) {
            return await this.createWallet(command);
        }

        // List Wallets
        if (lowerCommand.includes('show wallets') || lowerCommand.includes('list wallets') || lowerCommand.includes('get wallets')) {
            return await this.listWallets();
        }

        // Check Balance
        if (lowerCommand.includes('check balance') || lowerCommand.includes('show balance') || lowerCommand.includes('get balance')) {
            return await this.checkBalance(command);
        }

        // Deposit
        if (lowerCommand.includes('deposit')) {
            return await this.deposit(command);
        }

        // Transfer
        if (lowerCommand.includes('transfer') || lowerCommand.includes('send money')) {
            return await this.transfer(command);
        }

        // List Transactions
        if (lowerCommand.includes('show transactions') || lowerCommand.includes('list transactions') || lowerCommand.includes('transaction history')) {
            return await this.listTransactions();
        }

        // Help
        if (lowerCommand.includes('help') || lowerCommand.includes('what can you do')) {
            return this.showHelp();
        }

        return { message: "I didn't understand that command. Try saying 'help' to see what I can do." };
    }

    // API Integration Methods

    async createUser(command) {
        // Extract username and email from command
        const nameMatch = command.match(/(?:named|called)\s+(\w+)/i);
        const emailMatch = command.match(/(?:email|e-mail)\s+([\w.]+@[\w.]+)/i);

        if (!nameMatch) {
            return { message: "Please specify a username. For example: 'Create user named John with email john@example.com'" };
        }

        const username = nameMatch[1];
        const email = emailMatch ? emailMatch[1] : `${username.toLowerCase()}@example.com`;

        const response = await fetch('/api/v1/users/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Failed to create user');
        }

        return { message: `Successfully created user ${username} with ID ${data.id} and email ${email}` };
    }

    async listUsers() {
        const response = await fetch('/api/v1/users/');
        const users = await response.json();

        if (!response.ok) {
            throw new Error('Failed to fetch users');
        }

        if (users.length === 0) {
            return { message: 'No users found in the system.' };
        }

        const userList = users.map(u => `${u.username} (ID: ${u.id})`).join(', ');
        return { message: `Found ${users.length} user${users.length > 1 ? 's' : ''}: ${userList}` };
    }

    async createWallet(command) {
        // Extract user ID and PIN
        const userIdMatch = command.match(/(?:user|id)\s+(\d+)/i);
        const pinMatch = command.match(/(?:pin|code)\s+(\d{4})/i);

        if (!userIdMatch) {
            return { message: "Please specify a user ID. For example: 'Create wallet for user 1 with PIN 1234'" };
        }

        if (!pinMatch) {
            return { message: "Please specify a 4-digit PIN. For example: 'Create wallet for user 1 with PIN 1234'" };
        }

        const userId = parseInt(userIdMatch[1]);
        const pin = pinMatch[1];

        const response = await fetch('/api/v1/wallets/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId, pin })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Failed to create wallet');
        }

        return { message: `Successfully created wallet with ID ${data.id} for user ${userId}` };
    }

    async listWallets() {
        const response = await fetch('/api/v1/wallets/');
        const wallets = await response.json();

        if (!response.ok) {
            throw new Error('Failed to fetch wallets');
        }

        if (wallets.length === 0) {
            return { message: 'No wallets found in the system.' };
        }

        const walletList = wallets.map(w => `Wallet ${w.id} (User ${w.user_id}, Balance: $${w.balance})`).join(', ');
        return { message: `Found ${wallets.length} wallet${wallets.length > 1 ? 's' : ''}: ${walletList}` };
    }

    async checkBalance(command) {
        // Extract wallet ID
        const walletIdMatch = command.match(/(?:wallet|id)\s+(\d+)/i);

        if (!walletIdMatch) {
            return { message: "Please specify a wallet ID. For example: 'Check balance for wallet 1'" };
        }

        const walletId = parseInt(walletIdMatch[1]);

        const response = await fetch(`/api/v1/wallets/${walletId}`);
        const wallet = await response.json();

        if (!response.ok) {
            throw new Error(wallet.detail || 'Failed to fetch wallet balance');
        }

        return { message: `Wallet ${walletId} has a balance of $${wallet.balance}` };
    }

    async deposit(command) {
        // Extract wallet ID, amount, and PIN
        const walletIdMatch = command.match(/(?:wallet|to)\s+(\d+)/i);
        const amountMatch = command.match(/\$?(\d+(?:\.\d{2})?)/);
        const pinMatch = command.match(/(?:pin|code)\s+(\d{4})/i);

        if (!walletIdMatch) {
            return { message: "Please specify a wallet ID. For example: 'Deposit $100 to wallet 1 with PIN 1234'" };
        }

        if (!amountMatch) {
            return { message: "Please specify an amount. For example: 'Deposit $100 to wallet 1 with PIN 1234'" };
        }

        if (!pinMatch) {
            return { message: "Please specify the wallet PIN. For example: 'Deposit $100 to wallet 1 with PIN 1234'" };
        }

        const walletId = parseInt(walletIdMatch[1]);
        const amount = parseFloat(amountMatch[1]);
        const pin = pinMatch[1];

        const response = await fetch('/api/v1/wallets/deposit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ wallet_id: walletId, amount, pin })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Failed to deposit funds');
        }

        // SECURITY: Don't speak the PIN in the response
        return { message: `Successfully deposited $${amount} to wallet ${walletId}. New balance: $${data.balance}. PIN verified securely.` };
    }

    async transfer(command) {
        // Extract from wallet, to wallet, amount, and PIN
        const fromMatch = command.match(/(?:from|wallet)\s+(\d+)/i);
        const toMatch = command.match(/(?:to|wallet)\s+(\d+)/i);
        const amountMatch = command.match(/\$?(\d+(?:\.\d{2})?)/);
        const pinMatch = command.match(/(?:pin|code)\s+(\d{4})/i);

        if (!fromMatch || !toMatch) {
            return { message: "Please specify both sender and receiver wallets. For example: 'Transfer $50 from wallet 1 to wallet 2 with PIN 1234'" };
        }

        if (!amountMatch) {
            return { message: "Please specify an amount. For example: 'Transfer $50 from wallet 1 to wallet 2 with PIN 1234'" };
        }

        if (!pinMatch) {
            return { message: "Please specify the sender's PIN. For example: 'Transfer $50 from wallet 1 to wallet 2 with PIN 1234'" };
        }

        const fromWalletId = parseInt(fromMatch[1]);
        const toWalletId = parseInt(toMatch[1]);
        const amount = parseFloat(amountMatch[1]);
        const pin = pinMatch[1];

        const response = await fetch('/api/v1/transfer/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                from_wallet_id: fromWalletId,
                to_wallet_id: toWalletId,
                amount,
                pin
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Failed to transfer funds');
        }

        // SECURITY: Don't speak the PIN in the response
        return { message: `Successfully transferred $${amount} from wallet ${fromWalletId} to wallet ${toWalletId}. Transaction completed securely.` };
    }

    async listTransactions() {
        const response = await fetch('/api/v1/transfer/transactions');
        const transactions = await response.json();

        if (!response.ok) {
            throw new Error('Failed to fetch transactions');
        }

        if (transactions.length === 0) {
            return { message: 'No transactions found in the system.' };
        }

        const recentTxns = transactions.slice(-5);
        const txnList = recentTxns.map(t =>
            `$${t.amount} from wallet ${t.from_wallet_id} to wallet ${t.to_wallet_id}`
        ).join(', ');

        return { message: `Found ${transactions.length} total transactions. Most recent: ${txnList}` };
    }

    showHelp() {
        const helpText = `I can help you with the following commands: 
        Create user named John with email john@example.com. 
        Show all users. 
        Create wallet for user 1 with PIN 1234. 
        Show all wallets. 
        Check balance for wallet 1. 
        Deposit $100 to wallet 1 with PIN 1234. 
        Transfer $50 from wallet 1 to wallet 2 with PIN 1234. 
        Show transactions.`;

        return { message: helpText };
    }

    // UI Helper Methods

    speak(text) {
        if (!this.synthesis) return;

        // Cancel any ongoing speech
        this.synthesis.cancel();

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 1.0;
        utterance.pitch = 1.0;
        utterance.volume = 1.0;

        this.synthesis.speak(utterance);
    }

    addToConversation(role, message) {
        this.conversationHistory.push({ role, message, timestamp: new Date() });
        this.updateConversationUI();
    }

    updateConversationUI() {
        const container = document.getElementById('conversationHistory');
        if (!container) return;

        container.innerHTML = this.conversationHistory.map(item => {
            const icon = item.role === 'user' ? '👤' : item.role === 'assistant' ? '🤖' : '⚙️';
            const className = `conversation-item ${item.role}`;
            return `
                <div class="${className}">
                    <span class="icon">${icon}</span>
                    <div class="message">${this.escapeHtml(item.message)}</div>
                </div>
            `;
        }).join('');

        // Scroll to bottom
        container.scrollTop = container.scrollHeight;
    }

    updateUIState(state) {
        const micButton = document.getElementById('micButton');
        const statusText = document.getElementById('statusText');

        if (!micButton || !statusText) return;

        micButton.className = 'mic-button';

        switch (state) {
            case 'listening':
                micButton.classList.add('listening');
                statusText.textContent = '🎤 Listening...';
                break;
            case 'processing':
                micButton.classList.add('processing');
                statusText.textContent = '⚙️ Processing...';
                break;
            default:
                statusText.textContent = '💬 Click the microphone to speak';
        }
    }

    showError(message) {
        const errorDiv = document.getElementById('errorMessage');
        if (errorDiv) {
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
            setTimeout(() => {
                errorDiv.style.display = 'none';
            }, 5000);
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    clearConversation() {
        this.conversationHistory = [];
        this.updateConversationUI();
    }
}

// Initialize voice assistant when page loads
let voiceAssistant;

document.addEventListener('DOMContentLoaded', () => {
    voiceAssistant = new VoiceAssistant();

    // Setup mic button
    const micButton = document.getElementById('micButton');
    if (micButton) {
        micButton.addEventListener('click', () => {
            voiceAssistant.startListening();
        });
    }

    // Setup clear button
    const clearButton = document.getElementById('clearConversation');
    if (clearButton) {
        clearButton.addEventListener('click', () => {
            voiceAssistant.clearConversation();
        });
    }
});
