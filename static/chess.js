// Global variables to track game state
let selectedPiece = null;      // Currently selected chess piece
let selectedSquare = null;     // Square containing the selected piece
let isGameOver = false;        // Track if the game has ended
let canPlayerMove = true;      // Track if the player can make a move
const playerColor = document.querySelector('.chess-board').dataset.playerColor;  // Player's chosen color (white/black)

/**
 * Clears the currently selected piece and square
 * Removes visual highlighting from the board
 */
function clearSelection() {
    if (selectedSquare) {
        selectedSquare.classList.remove('selected');
    }
    selectedPiece = null;
    selectedSquare = null;
}

/**
 * Handles clicking on a chess square
 * Manages piece selection and move validation
 * @param {Event} e - Click event
 */
function handleSquareClick(e) {
    // Prevent moves if game is over
    if (isGameOver) {
        showMoveStatus('Game is over! Start a new game.', false);
        return;
    }

    const clickedSquare = e.target.closest('.square');
    const clickedPiece = clickedSquare.querySelector('.piece');

    // First click - Selecting a piece
    if (!selectedPiece) {
        // Ignore clicks on empty squares
        if (clickedPiece.textContent.trim() === '') {
            return;
        }

        // Validate piece color and turn
        const pieceColor = getPieceColor(clickedPiece.textContent);
        const currentTurn = document.getElementById('turn-indicator').textContent.split(' ')[0].toLowerCase();

        if (pieceColor !== currentTurn || pieceColor !== playerColor) {
            showMoveStatus(`It's ${currentTurn}'s turn to move!`, false);
            return;
        }

        // Select the piece
        selectedPiece = clickedPiece;
        selectedSquare = clickedSquare;
        selectedSquare.classList.add('selected');
    } 
    // Second click - Moving the piece or reselecting
    else {
        // Prevent making the move if AI is thinking
        if (!canPlayerMove) {
            showMoveStatus('Please wait for Black to make a move before proceeding.', false);
            return;
        }

        // Clicking the same square deselects the piece
        if (clickedSquare === selectedSquare) {
            clearSelection();
            return;
        }

        // Check if clicking another piece of the same color
        const clickedPieceContent = clickedPiece.textContent.trim();
        if (clickedPieceContent !== '') {
            const clickedPieceColor = getPieceColor(clickedPieceContent);
            const selectedPieceColor = getPieceColor(selectedPiece.textContent);
            
            // If clicking another piece of the same color, reselect it
            if (clickedPieceColor === selectedPieceColor) {
                clearSelection();
                selectedPiece = clickedPiece;
                selectedSquare = clickedSquare;
                selectedSquare.classList.add('selected');
                return;
            }
        }

        // Attempt to make the move
        const fromRow = parseInt(selectedSquare.dataset.row);
        const fromCol = parseInt(selectedSquare.dataset.col);
        const toRow = parseInt(clickedSquare.dataset.row);
        const toCol = parseInt(clickedSquare.dataset.col);

        makeMove(fromRow, fromCol, toRow, toCol, selectedPiece, clickedSquare.querySelector('.piece'));
        clearSelection();
    }
}

/**
 * Initiates a chess move and communicates with the server
 * @param {number} fromRow - Starting row
 * @param {number} fromCol - Starting column
 * @param {number} toRow - Target row
 * @param {number} toCol - Target column
 * @param {Element} fromPiece - Piece being moved
 * @param {Element} toPiece - Piece at target square (if any)
 */
function isCastlingAttempt(fromPiece, fromCol, toCol) {
    return get_piece_type(fromPiece.textContent) === 'king' && Math.abs(toCol - fromCol) === 2;
}

function isPathClear(row, fromCol, toCol) {
    const step = fromCol < toCol ? 1 : -1;
    for (let col = fromCol + step; col !== toCol; col += step) {
        const square = document.querySelector(`.square[data-row="${row}"][data-col="${col}"]`);
        if (square.querySelector('.piece').textContent.trim() !== '') {
            return false;
        }
    }
    return true;
}

function get_piece_type(piece) {
    const pieceTypes = {
        '♔': 'king', '♚': 'king',
        '♕': 'queen', '♛': 'queen',
        '♖': 'rook', '♜': 'rook',
        '♗': 'bishop', '♝': 'bishop',
        '♘': 'knight', '♞': 'knight',
        '♙': 'pawn', '♟': 'pawn'
    };
    return pieceTypes[piece] || null;
}

function makeMove(fromRow, fromCol, toRow, toCol, fromPiece, toPiece) {
    // Store original board state for move reversal if needed
    const originalFromContent = fromPiece.textContent;
    const originalToContent = toPiece.textContent;

    // Check if this is a castling attempt
    const isCastling = isCastlingAttempt(fromPiece, fromCol, toCol);
    
    let castlingState = null;
    if (isCastling) {
        // Quick frontend validation for castling
        const isQueenside = toCol < fromCol;
        const rookCol = isQueenside ? 0 : 7;
        const rookSquare = document.querySelector(`.square[data-row="${fromRow}"][data-col="${rookCol}"]`);
        const rookPiece = rookSquare.querySelector('.piece');
        const expectedRook = playerColor === 'white' ? '♖' : '♜';
        
        if (rookPiece.textContent !== expectedRook || !isPathClear(fromRow, fromCol, toCol)) {
            showMoveStatus('Invalid castling move! Path must be clear.', false);
            return;
        }

        const newRookCol = toCol + (isQueenside ? 1 : -1);
        const newRookSquare = document.querySelector(`.square[data-row="${fromRow}"][data-col="${newRookCol}"]`);
        
        // Store castling state for potential reversal
        castlingState = {
            rookSquare,
            rookPiece,
            newRookSquare,
            originalKingContent: fromPiece.textContent,
            originalKingSquareContent: '',
            originalRookContent: rookPiece.textContent,
            originalNewRookSquareContent: newRookSquare.querySelector('.piece').textContent
        };

        // Update UI for king with animation
        fromPiece.style.transition = 'all 0.3s ease-out';
        toPiece.style.transition = 'all 0.3s ease-out';
        
        fromPiece.style.opacity = '0';
        toPiece.style.opacity = '0';
        fromPiece.style.transform = 'translate(-50%, -50%) scale(0.8)';
        toPiece.style.transform = 'translate(-50%, -50%) scale(1.2)';
        
        setTimeout(() => {
            toPiece.textContent = fromPiece.textContent;
            fromPiece.textContent = '';
            
            fromPiece.style.opacity = '1';
            toPiece.style.opacity = '1';
            fromPiece.style.transform = 'translate(-50%, -50%) scale(1)';
            toPiece.style.transform = 'translate(-50%, -50%) scale(1)';
            
            setTimeout(() => {
                fromPiece.style.transition = '';
                toPiece.style.transition = '';
                fromPiece.style.transform = 'translate(-50%, -50%)';
                toPiece.style.transform = 'translate(-50%, -50%)';
            }, 300);
        }, 300);

        // Update UI for rook with animation
        rookPiece.style.transition = 'all 0.3s ease-out';
        newRookSquare.querySelector('.piece').style.transition = 'all 0.3s ease-out';
        
        rookPiece.style.opacity = '0';
        newRookSquare.querySelector('.piece').style.opacity = '0';
        rookPiece.style.transform = 'translate(-50%, -50%) scale(0.8)';
        newRookSquare.querySelector('.piece').style.transform = 'translate(-50%, -50%) scale(1.2)';
        
        setTimeout(() => {
            newRookSquare.querySelector('.piece').textContent = rookPiece.textContent;
            rookPiece.textContent = '';
            
            rookPiece.style.opacity = '1';
            newRookSquare.querySelector('.piece').style.opacity = '1';
            rookPiece.style.transform = 'translate(-50%, -50%) scale(1)';
            newRookSquare.querySelector('.piece').style.transform = 'translate(-50%, -50%) scale(1)';
            
            setTimeout(() => {
                rookPiece.style.transition = '';
                newRookSquare.querySelector('.piece').style.transition = '';
                rookPiece.style.transform = 'translate(-50%, -50%)';
                newRookSquare.querySelector('.piece').style.transform = 'translate(-50%, -50%)';
            }, 300);
        }, 300);
    } else {
        // Update UI for regular moves with animation
        fromPiece.style.transition = 'all 0.3s ease-out';
        toPiece.style.transition = 'all 0.3s ease-out';
        
        fromPiece.style.opacity = '0';
        toPiece.style.opacity = '0';
        fromPiece.style.transform = 'translate(-50%, -50%) scale(0.8)';
        toPiece.style.transform = 'translate(-50%, -50%) scale(1.2)';
        
        setTimeout(() => {
            toPiece.textContent = fromPiece.textContent;
            fromPiece.textContent = '';
            
            fromPiece.style.opacity = '1';
            toPiece.style.opacity = '1';
            fromPiece.style.transform = 'translate(-50%, -50%) scale(1)';
            toPiece.style.transform = 'translate(-50%, -50%) scale(1)';
            
            setTimeout(() => {
                fromPiece.style.transition = '';
                toPiece.style.transition = '';
                fromPiece.style.transform = 'translate(-50%, -50%)';
                toPiece.style.transform = 'translate(-50%, -50%)';
            }, 300);
        }, 300);
    }

    // Show AI thinking indicator with delay
    const thinkingTimeout = setTimeout(() => {
        showAIThinking();
        canPlayerMove = false;  // Disable player moves while AI is thinking
    }, 500);

    // Send move to server for validation and AI response
    fetch('/move', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            from_row: fromRow,
            from_col: fromCol,
            to_row: toRow,
            to_col: toCol
        })
    })
    .then(response => response.json())
    .then(data => {
        // Hide AI thinking indicator
        clearTimeout(thinkingTimeout);
        hideAIThinking();
        canPlayerMove = true;  // Re-enable player moves after AI responds

        if (data.valid) {
            handleValidMove(data);
        } else {
            // Revert move UI if invalid
            if (isCastling && castlingState) {
                // Revert king
                fromPiece.textContent = castlingState.originalKingContent;
                toPiece.textContent = castlingState.originalKingSquareContent;
                
                // Revert rook with animation
                castlingState.rookPiece.style.transition = 'opacity 0.3s';
                castlingState.newRookSquare.querySelector('.piece').style.transition = 'opacity 0.3s';
                
                castlingState.rookPiece.style.opacity = '0';
                castlingState.newRookSquare.querySelector('.piece').style.opacity = '0';
                
                setTimeout(() => {
                    castlingState.rookPiece.textContent = castlingState.originalRookContent;
                    castlingState.newRookSquare.querySelector('.piece').textContent = castlingState.originalNewRookSquareContent;
                    
                    castlingState.rookPiece.style.opacity = '1';
                    castlingState.newRookSquare.querySelector('.piece').style.opacity = '1';
                    
                    setTimeout(() => {
                        castlingState.rookPiece.style.transition = '';
                        castlingState.newRookSquare.querySelector('.piece').style.transition = '';
                    }, 300);
                }, 300);
            } else {
                // Revert regular move
                fromPiece.textContent = originalFromContent;
                toPiece.textContent = originalToContent;
            }
            showMoveStatus(data.message, false);
        }
    })
    .catch(error => {
        // Handle errors and revert move
        clearTimeout(thinkingTimeout);
        hideAIThinking();
        fromPiece.textContent = originalFromContent;
        toPiece.textContent = originalToContent;
        console.error('Error:', error);
        showMoveStatus('Error making move!', false);
    });

    console.log(`Attempting to move from (${fromRow}, ${fromCol}) to (${toRow}, ${toCol})`);

    // Check if the move is a castling move
    if (fromPiece.textContent === '♔' && Math.abs(toCol - fromCol) === 2) {
        console.log('Castling move detected.');
    }
}

/**
 * Processes server response after a valid move
 * Updates game state, UI, and displays analysis
 * @param {Object} data - Server response data
 */
function animateRookMove(castlingInfo) {
    const rookFromSquare = document.querySelector(
        `.square[data-row="${castlingInfo.row}"][data-col="${castlingInfo.rook_from_col}"]`
    );
    const rookToSquare = document.querySelector(
        `.square[data-row="${castlingInfo.row}"][data-col="${castlingInfo.rook_to_col}"]`
    );

    if (rookFromSquare && rookToSquare) {
        const rookPiece = rookFromSquare.querySelector('.piece');
        const targetSpot = rookToSquare.querySelector('.piece');
        
        // Set up animation
        rookPiece.style.transition = 'all 0.3s ease-out';
        targetSpot.style.transition = 'all 0.3s ease-out';
        
        // Fade out and scale
        rookPiece.style.opacity = '0';
        targetSpot.style.opacity = '0';
        rookPiece.style.transform = 'translate(-50%, -50%) scale(0.8)';
        targetSpot.style.transform = 'translate(-50%, -50%) scale(1.2)';
        
        // Move the rook piece
        setTimeout(() => {
            targetSpot.textContent = rookPiece.textContent;
            rookPiece.textContent = '';
            
            // Fade in and normalize scale
            rookPiece.style.opacity = '1';
            targetSpot.style.opacity = '1';
            rookPiece.style.transform = 'translate(-50%, -50%) scale(1)';
            targetSpot.style.transform = 'translate(-50%, -50%) scale(1)';
            
            // Clean up transitions
            setTimeout(() => {
                rookPiece.style.transition = '';
                targetSpot.style.transition = '';
                rookPiece.style.transform = 'translate(-50%, -50%)';
                targetSpot.style.transform = 'translate(-50%, -50%)';
            }, 300);
        }, 300);
    }
}

function handleValidMove(data) {
    const turnIndicator = document.getElementById('turn-indicator');
    
    // Log the move details
    // Display move analysis if available
    if (data.move_analysis) {
        showMoveAnalysis(data.move_analysis, data.ai_move_analysis);
    }

    // Handle castling if applicable
    if (data.castling_info) {
        setTimeout(() => animateRookMove(data.castling_info), 300);
    }
    
    if (data.game_over) {
        // Handle game over state
        isGameOver = true;
        turnIndicator.textContent = `${data.winner} wins!`;
        turnIndicator.classList.add('game-over');
        turnIndicator.classList.remove('in-check');
        showMoveStatus(data.message, true);
        document.getElementById('new-game-btn').disabled = true;
    } else {
        // Handle AI's move if present
        if (data.ai_move) {
            showAIMove(data.ai_move);
            // Handle AI castling if applicable
            if (data.ai_move && data.ai_move.castling_info) {
                setTimeout(() => animateRookMove(data.ai_move.castling_info), 600);
            }
            turnIndicator.textContent = 
                `${data.current_turn.charAt(0).toUpperCase() + data.current_turn.slice(1)} to move (You are ${playerColor})`;
            
            // Update check status
            if (data.in_check) {
                turnIndicator.classList.add('in-check');
                showMoveStatus(data.message, true);
            } else {
                turnIndicator.classList.remove('in-check');
            }
        }
    }
}

/**
 * Displays move analysis for both player and AI
 * @param {string} playerAnalysis - Analysis of player's move
 * @param {string} aiAnalysis - Analysis of AI's move
 */
function showMoveAnalysis(playerAnalysis, aiAnalysis) {
    const container = document.getElementById('analysis-container');
    const playerContent = document.getElementById('analysis-content');
    const aiContainer = document.getElementById('ai-analysis');
    const aiContent = document.getElementById('ai-analysis-content');
    
    // Update player's analysis
    playerContent.textContent = playerAnalysis;
    
    // Update AI's analysis if available
    if (aiAnalysis) {
        aiContainer.style.display = 'block';
        aiContent.textContent = aiAnalysis;
    } else {
        aiContainer.style.display = 'none';
    }
    
    container.style.display = 'block';
}

/**
 * Shows temporary status messages
 * @param {string} message - Status message to display
 * @param {boolean} success - Whether the message indicates success
 */
function showMoveStatus(message, success) {
    const statusDiv = document.getElementById('move-status');
    statusDiv.textContent = message;
    statusDiv.className = success ? 'success' : 'error';
    statusDiv.style.display = 'block';
    setTimeout(() => {
        statusDiv.style.display = 'none';
    }, 2000);
}

/**
 * Handles game restart
 * Confirms with user before reloading
 */
function startNewGame() {
    if (!isGameOver && !confirm('Are you sure you want to start a new game?')) {
        return;
    }
    location.reload();
}

/**
 * Determines the color of a chess piece
 * @param {string} piece - Unicode chess piece character
 * @returns {string|null} Color of the piece ('white'/'black') or null
 */
function getPieceColor(piece) {
    const whitePieces = '♔♕♖♗♘♙';
    const blackPieces = '♚♛♜♝♞♟';
    if (whitePieces.includes(piece)) return 'white';
    if (blackPieces.includes(piece)) return 'black';
    return null;
}

/**
 * Displays and animates AI's move on the board
 * @param {Object} move - AI move coordinates
 */
function showAIMove(move) {
    if (!move) return;
    
    // Clear any existing highlights
    document.querySelectorAll('.ai-move-highlight').forEach(square => {
        square.classList.remove('ai-move-highlight');
    });
    
    // Get source and target squares
    const fromSquare = document.querySelector(
        `.square[data-row="${move.from_row}"][data-col="${move.from_col}"]`
    );
    const toSquare = document.querySelector(
        `.square[data-row="${move.to_row}"][data-col="${move.to_col}"]`
    );
    
    if (fromSquare && toSquare) {
        // Highlight the move
        fromSquare.classList.add('ai-move-highlight');
        toSquare.classList.add('ai-move-highlight');
        
        // Get pieces for animation
        const fromPiece = fromSquare.querySelector('.piece');
        const toPiece = toSquare.querySelector('.piece');
        const pieceToMove = fromPiece.textContent;
        
        // Set up animation
        fromPiece.style.transition = 'all 0.3s ease-out';
        toPiece.style.transition = 'all 0.3s ease-out';
        
        // Fade out and scale
        fromPiece.style.opacity = '0';
        toPiece.style.opacity = '0';
        fromPiece.style.transform = 'translate(-50%, -50%) scale(0.8)';
        toPiece.style.transform = 'translate(-50%, -50%) scale(1.2)';
        
        // Update pieces after fade
        setTimeout(() => {
            fromPiece.textContent = '';
            toPiece.textContent = pieceToMove;
            
            // Fade in and normalize scale
            fromPiece.style.opacity = '1';
            toPiece.style.opacity = '1';
            fromPiece.style.transform = 'translate(-50%, -50%) scale(1)';
            toPiece.style.transform = 'translate(-50%, -50%) scale(1)';
            
            // Clean up transitions
            setTimeout(() => {
                fromPiece.style.transition = '';
                toPiece.style.transition = '';
                fromPiece.style.transform = 'translate(-50%, -50%)';
                toPiece.style.transform = 'translate(-50%, -50%)';
            }, 300);
        }, 300);
        
        // Remove highlights after delay
        setTimeout(() => {
            fromSquare.classList.remove('ai-move-highlight');
            toSquare.classList.remove('ai-move-highlight');
        }, 2000);
    }
}

/**
 * Shows the AI thinking indicator
 * Fades out turn indicator and fades in thinking animation
 */
function showAIThinking() {
    document.getElementById('turn-indicator').style.opacity = '0';
    const aiThinking = document.getElementById('ai-thinking');
    aiThinking.style.display = 'flex';
    // Force a reflow for smooth animation
    void aiThinking.offsetWidth;
    aiThinking.classList.add('visible');
}

/**
 * Hides the AI thinking indicator
 * Fades out thinking animation and fades in turn indicator
 */
function hideAIThinking() {
    document.getElementById('turn-indicator').style.opacity = '1';
    const aiThinking = document.getElementById('ai-thinking');
    aiThinking.classList.remove('visible');
    setTimeout(() => {
        aiThinking.style.display = 'none';
    }, 200);
}

// Initialize game state and event listeners
document.getElementById('new-game-btn').disabled = isGameOver;

// Add click handlers for squares
document.querySelectorAll('.square').forEach(square => {
    square.addEventListener('click', handleSquareClick);
    square.addEventListener('dragover', handleDragOver);
    square.addEventListener('drop', handleDrop);
});

// Add drag-and-drop handlers for pieces
document.querySelectorAll('.piece').forEach(piece => {
    piece.addEventListener('dragstart', handleDragStart);
    piece.addEventListener('dragend', handleDragEnd);
});

/**
 * Handles the start of a drag operation
 * Validates the move and updates visual state
 * @param {DragEvent} e - Drag start event
 */
function handleDragStart(e) {
    if (isGameOver) {
        e.preventDefault();
        showMoveStatus('Game is over! Start a new game.', false);
        return;
    }

    const piece = e.target;
    if (piece.textContent.trim() === '') {
        e.preventDefault();
        return;
    }

    const pieceColor = getPieceColor(piece.textContent);
    const currentTurn = document.getElementById('turn-indicator').textContent.split(' ')[0].toLowerCase();
    
    if (pieceColor !== currentTurn || pieceColor !== playerColor) {
        e.preventDefault();
        showMoveStatus(`It's ${currentTurn}'s turn to move!`, false);
        return;
    }

    e.target.classList.add('dragging');
    selectedPiece = e.target;
    selectedSquare = e.target.parentElement;
    selectedSquare.classList.add('selected');
}

/**
 * Handles the end of a drag operation
 * Cleans up visual state
 * @param {DragEvent} e - Drag end event
 */
function handleDragEnd(e) {
    e.target.classList.remove('dragging');
    if (selectedSquare) {
        selectedSquare.classList.remove('selected');
    }
    clearSelection();
}

/**
 * Allows dropping on squares
 * @param {DragEvent} e - Drag over event
 */
function handleDragOver(e) {
    e.preventDefault();
}

/**
 * Handles piece drops on squares
 * Validates and executes the move
 * @param {DragEvent} e - Drop event
 */
function handleDrop(e) {
    e.preventDefault();
    const targetSquare = e.target.closest('.square');
    if (!targetSquare || !selectedPiece) return;

    // Check if the destination square contains an opponent's piece
    const destinationPiece = targetSquare.querySelector('.piece').textContent.trim();
    if (destinationPiece !== '') {
        const destinationPieceColor = getPieceColor(destinationPiece);
        const selectedPieceColor = getPieceColor(selectedPiece.textContent);
        
        // If destination has a piece of the same color, invalid move
        if (destinationPieceColor === selectedPieceColor) {
            showMoveStatus('Invalid move! Cannot capture your own piece.', false);
            clearSelection();
            return;
        }
    }

    const fromRow = parseInt(selectedSquare.dataset.row);
    const fromCol = parseInt(selectedSquare.dataset.col);
    const toRow = parseInt(targetSquare.dataset.row);
    const toCol = parseInt(targetSquare.dataset.col);

    makeMove(fromRow, fromCol, toRow, toCol, selectedPiece, targetSquare.querySelector('.piece'));
    clearSelection();
}
