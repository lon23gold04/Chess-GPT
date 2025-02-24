// Game state management
const gameState = {
    selectedPiece: null,
    selectedSquare: null,
    isGameOver: false,
    canPlayerMove: true,
    playerColor: document.querySelector('.chess-board').dataset.playerColor
};

// Constants 
const ANIMATION = {
    DURATION: 300,
    STYLE: 'all 0.3s ease-out'
};

// Piece type and color mapping
const PIECE_TYPES = {
    '♔': 'king', '♚': 'king',
    '♕': 'queen', '♛': 'queen',
    '♖': 'rook', '♜': 'rook',
    '♗': 'bishop', '♝': 'bishop',
    '♘': 'knight', '♞': 'knight',
    '♙': 'pawn', '♟': 'pawn'
};

const WHITE_PIECES = '♔♕♖♗♘♙';
const BLACK_PIECES = '♚♛♜♝♞♟';

/**
 * Utility functions
 */
const utils = {
    // Get piece color (white/black/null)
    getPieceColor(piece) {
        if (WHITE_PIECES.includes(piece)) return 'white';
        if (BLACK_PIECES.includes(piece)) return 'black';
        return null;
    },
    
    // Get piece type (king/queen/etc)
    getPieceType(piece) {
        return PIECE_TYPES[piece] || null;
    },
    
    // Is castling attempt
    isCastlingAttempt(fromPiece, fromCol, toCol) {
        return utils.getPieceType(fromPiece.textContent) === 'king' && Math.abs(toCol - fromCol) === 2;
    },
    
    // Check if path is clear (for castling)
    isPathClear(row, fromCol, toCol) {
        const step = fromCol < toCol ? 1 : -1;
        for (let col = fromCol + step; col !== toCol; col += step) {
            const square = document.querySelector(`.square[data-row="${row}"][data-col="${col}"]`);
            if (square.querySelector('.piece').textContent.trim() !== '') {
                return false;
            }
        }
        return true;
    }
};

/**
 * UI manipulation functions
 */
const ui = {
    // Show status message 
    showStatus(message, success) {
        const statusDiv = document.getElementById('move-status');
        statusDiv.textContent = message;
        statusDiv.className = success ? 'success' : 'error';
        statusDiv.style.display = 'block';
        setTimeout(() => statusDiv.style.display = 'none', 2000);
    },
    
    // Toggle AI thinking indicator
    toggleAIThinking(show) {
        document.getElementById('turn-indicator').style.opacity = show ? '0' : '1';
        const aiThinking = document.getElementById('ai-thinking');
        
        if (show) {
            aiThinking.style.display = 'flex';
            void aiThinking.offsetWidth; // Force reflow
            aiThinking.classList.add('visible');
        } else {
            aiThinking.classList.remove('visible');
            setTimeout(() => aiThinking.style.display = 'none', 200);
        }
    },
    
    // Show move analysis
    showAnalysis(playerAnalysis, aiAnalysis) {
        const container = document.getElementById('analysis-container');
        const playerContent = document.getElementById('analysis-content');
        const aiContainer = document.getElementById('ai-analysis');
        const aiContent = document.getElementById('ai-analysis-content');
        
        playerContent.textContent = playerAnalysis;
        
        if (aiAnalysis) {
            aiContainer.style.display = 'block';
            aiContent.textContent = aiAnalysis;
        } else {
            aiContainer.style.display = 'none';
        }
        
        container.style.display = 'block';
    },
    
    // Clear selection state
    clearSelection() {
        if (gameState.selectedSquare) {
            gameState.selectedSquare.classList.remove('selected');
        }
        gameState.selectedPiece = null;
        gameState.selectedSquare = null;
    },
    
    // Update game over state
    setGameOver(data) {
        const turnIndicator = document.getElementById('turn-indicator');
        gameState.isGameOver = true;
        turnIndicator.textContent = `${data.winner} wins!`;
        turnIndicator.classList.add('game-over');
        turnIndicator.classList.remove('in-check');
        ui.showStatus(data.message, true);
        document.getElementById('new-game-btn').disabled = true;
    },
    
    // Update turn indicator
    updateTurnIndicator(currentTurn, inCheck) {
        const turnIndicator = document.getElementById('turn-indicator');
        turnIndicator.textContent = `${currentTurn.charAt(0).toUpperCase() + currentTurn.slice(1)} to move (You are ${gameState.playerColor})`;
        
        if (inCheck) {
            turnIndicator.classList.add('in-check');
        } else {
            turnIndicator.classList.remove('in-check');
        }
    }
};

/**
 * Animation functions
 */
const animations = {
    // Animate piece movement
    animatePiece(fromElement, toElement, onComplete) {
        const elements = [fromElement, toElement];
        elements.forEach(el => {
            el.style.transition = ANIMATION.STYLE;
            el.style.opacity = '0';
            el.style.transform = el === fromElement ? 
                'translate(-50%, -50%) scale(0.8)' : 
                'translate(-50%, -50%) scale(1.2)';
        });

        setTimeout(() => {
            onComplete();
            elements.forEach(el => {
                el.style.opacity = '1';
                el.style.transform = 'translate(-50%, -50%) scale(1)';
            });

            setTimeout(() => {
                elements.forEach(el => {
                    el.style.transition = '';
                    el.style.transform = 'translate(-50%, -50%)';
                });
            }, ANIMATION.DURATION);
        }, ANIMATION.DURATION);
    },
    
    // Animate rook for castling
    animateRook(castlingInfo) {
        const rookFromSquare = document.querySelector(
            `.square[data-row="${castlingInfo.row}"][data-col="${castlingInfo.rook_from_col}"]`
        );
        const rookToSquare = document.querySelector(
            `.square[data-row="${castlingInfo.row}"][data-col="${castlingInfo.rook_to_col}"]`
        );

        if (rookFromSquare && rookToSquare) {
            const rookPiece = rookFromSquare.querySelector('.piece');
            const targetSpot = rookToSquare.querySelector('.piece');
            
            this.animatePiece(rookPiece, targetSpot, () => {
                targetSpot.textContent = rookPiece.textContent;
                rookPiece.textContent = '';
            });
        }
    },
    
    // Highlight AI's move
    highlightAIMove(move) {
        if (!move) return;
        
        document.querySelectorAll('.ai-move-highlight').forEach(square => {
            square.classList.remove('ai-move-highlight');
        });
        
        const fromSquare = document.querySelector(
            `.square[data-row="${move.from_row}"][data-col="${move.from_col}"]`
        );
        const toSquare = document.querySelector(
            `.square[data-row="${move.to_row}"][data-col="${move.to_col}"]`
        );
        
        if (fromSquare && toSquare) {
            [fromSquare, toSquare].forEach(square => square.classList.add('ai-move-highlight'));
            
            const fromPiece = fromSquare.querySelector('.piece');
            const toPiece = toSquare.querySelector('.piece');
            const pieceToMove = fromPiece.textContent;
            
            this.animatePiece(fromPiece, toPiece, () => {
                toPiece.textContent = pieceToMove;
                fromPiece.textContent = '';
            });
            
            setTimeout(() => {
                [fromSquare, toSquare].forEach(square => 
                    square.classList.remove('ai-move-highlight')
                );
            }, 2000);
        }
    }
};

/**
 * Move handling
 */
const moveHandler = {
    // Attempt a move
    makeMove(fromRow, fromCol, toRow, toCol, fromPiece, toPiece) {
        // Prevent moves when AI is thinking
        if (!gameState.canPlayerMove) {
            ui.showStatus('Please wait for the opponent to complete their move.', false);
            return;
        }
        
        const originalFromContent = fromPiece.textContent;
        const originalToContent = toPiece.textContent;
        const isCastling = utils.isCastlingAttempt(fromPiece, fromCol, toCol);
        
        let castlingState = null;
        if (isCastling) {
            const isQueenside = toCol < fromCol;
            const rookCol = isQueenside ? 0 : 7;
            const rookSquare = document.querySelector(`.square[data-row="${fromRow}"][data-col="${rookCol}"]`);
            const rookPiece = rookSquare.querySelector('.piece');
            const expectedRook = gameState.playerColor === 'white' ? '♖' : '♜';
            
            if (rookPiece.textContent !== expectedRook || !utils.isPathClear(fromRow, fromCol, rookCol)) {
                ui.showStatus('Invalid castling move! Path must be clear.', false);
                return;
            }

            const newRookCol = toCol + (isQueenside ? 1 : -1);
            const newRookSquare = document.querySelector(`.square[data-row="${fromRow}"][data-col="${newRookCol}"]`);
            
            castlingState = {
                rookSquare,
                rookPiece,
                newRookSquare,
                originalKingContent: fromPiece.textContent,
                originalKingSquareContent: '',
                originalRookContent: rookPiece.textContent,
                originalNewRookSquareContent: newRookSquare.querySelector('.piece').textContent
            };

            // Animate king and rook
            animations.animatePiece(fromPiece, toPiece, () => {
                toPiece.textContent = fromPiece.textContent;
                fromPiece.textContent = '';
            });

            animations.animatePiece(rookPiece, newRookSquare.querySelector('.piece'), () => {
                newRookSquare.querySelector('.piece').textContent = rookPiece.textContent;
                rookPiece.textContent = '';
            });
        } else {
            // Regular move animation
            animations.animatePiece(fromPiece, toPiece, () => {
                toPiece.textContent = fromPiece.textContent;
                fromPiece.textContent = '';
            });
        }

        // Show AI thinking after a short delay
        const thinkingTimeout = setTimeout(() => {
            ui.toggleAIThinking(true);
            gameState.canPlayerMove = false;
        }, 500);

        // Send move to server
        fetch('/move', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ from_row: fromRow, from_col: fromCol, to_row: toRow, to_col: toCol })
        })
        .then(response => response.json())
        .then(data => {
            clearTimeout(thinkingTimeout);
            ui.toggleAIThinking(false);
            gameState.canPlayerMove = true;

            if (data.valid) {
                this.handleValidMove(data);
            } else {
                this.revertMove(isCastling, castlingState, fromPiece, toPiece, originalFromContent, originalToContent);
                ui.showStatus(data.message, false);
            }
        })
        .catch(error => {
            clearTimeout(thinkingTimeout);
            ui.toggleAIThinking(false);
            this.revertMove(isCastling, castlingState, fromPiece, toPiece, originalFromContent, originalToContent);
            console.error('Error:', error);
            ui.showStatus('Error making move!', false);
        });
    },
    
    // Handle valid move response
    handleValidMove(data) {
        // Display move analysis if available
        if (data.move_analysis) {
            ui.showAnalysis(data.move_analysis, data.ai_move_analysis);
        }

        // Handle castling if applicable
        if (data.castling_info) {
            setTimeout(() => animations.animateRook(data.castling_info), 300);
        }
        
        if (data.game_over) {
            // Handle game over state
            ui.setGameOver(data);
        } else {
            // Handle AI's move if present
            if (data.ai_move) {
                animations.highlightAIMove(data.ai_move);
                // Handle AI castling if applicable
                if (data.ai_move.castling_info) {
                    setTimeout(() => animations.animateRook(data.ai_move.castling_info), 600);
                }
                
                // Update turn indicator and check status
                ui.updateTurnIndicator(data.current_turn, data.in_check);
                
                if (data.in_check) {
                    ui.showStatus(data.message, true);
                }
            }
        }
    },
    
    // Revert move if invalid
    revertMove(isCastling, castlingState, fromPiece, toPiece, originalFromContent, originalToContent) {
        if (isCastling && castlingState) {
            fromPiece.textContent = castlingState.originalKingContent;
            toPiece.textContent = castlingState.originalKingSquareContent;
            
            animations.animatePiece(
                castlingState.rookPiece, 
                castlingState.newRookSquare.querySelector('.piece'),
                () => {
                    castlingState.rookPiece.textContent = castlingState.originalRookContent;
                    castlingState.newRookSquare.querySelector('.piece').textContent = 
                        castlingState.originalNewRookSquareContent;
                }
            );
        } else {
            fromPiece.textContent = originalFromContent;
            toPiece.textContent = originalToContent;
        }
    }
};

/**
 * Event handlers
 */
const eventHandlers = {
    // Handle square click
    handleSquareClick(e) {
        if (gameState.isGameOver) {
            ui.showStatus('Game is over! Start a new game.', false);
            return;
        }

        const clickedSquare = e.target.closest('.square');
        const clickedPiece = clickedSquare.querySelector('.piece');

        // First click - Selecting a piece
        if (!gameState.selectedPiece) {
            // Ignore clicks on empty squares
            if (clickedPiece.textContent.trim() === '') {
                return;
            }

            // Validate piece color and turn
            const pieceColor = utils.getPieceColor(clickedPiece.textContent);
            const currentTurn = document.getElementById('turn-indicator').textContent.split(' ')[0].toLowerCase();

            if (pieceColor !== currentTurn || pieceColor !== gameState.playerColor) {
                ui.showStatus(`It's ${currentTurn}'s turn to move!`, false);
                return;
            }

            // Select the piece
            gameState.selectedPiece = clickedPiece;
            gameState.selectedSquare = clickedSquare;
            gameState.selectedSquare.classList.add('selected');
        } 
        // Second click - Moving the piece or reselecting
        else {
            // Clicking the same square deselects the piece
            if (clickedSquare === gameState.selectedSquare) {
                ui.clearSelection();
                return;
            }

            // Check if clicking another piece of the same color
            const clickedPieceContent = clickedPiece.textContent.trim();
            if (clickedPieceContent !== '') {
                const clickedPieceColor = utils.getPieceColor(clickedPieceContent);
                const selectedPieceColor = utils.getPieceColor(gameState.selectedPiece.textContent);
                
                // If clicking another piece of the same color, reselect it
                if (clickedPieceColor === selectedPieceColor) {
                    ui.clearSelection();
                    gameState.selectedPiece = clickedPiece;
                    gameState.selectedSquare = clickedSquare;
                    gameState.selectedSquare.classList.add('selected');
                    return;
                }
            }

            // Attempt to make the move
            const fromRow = parseInt(gameState.selectedSquare.dataset.row);
            const fromCol = parseInt(gameState.selectedSquare.dataset.col);
            const toRow = parseInt(clickedSquare.dataset.row);
            const toCol = parseInt(clickedSquare.dataset.col);

            moveHandler.makeMove(fromRow, fromCol, toRow, toCol, gameState.selectedPiece, clickedPiece);
            ui.clearSelection();
        }
    },
    
    // Handle drag start
    handleDragStart(e) {
        if (gameState.isGameOver) {
            e.preventDefault();
            ui.showStatus('Game is over! Start a new game.', false);
            return;
        }

        const piece = e.target;
        if (piece.textContent.trim() === '') {
            e.preventDefault();
            return;
        }

        const pieceColor = utils.getPieceColor(piece.textContent);
        const currentTurn = document.getElementById('turn-indicator').textContent.split(' ')[0].toLowerCase();
        
        if (pieceColor !== currentTurn || pieceColor !== gameState.playerColor) {
            e.preventDefault();
            ui.showStatus(`It's ${currentTurn}'s turn to move!`, false);
            return;
        }

        e.target.classList.add('dragging');
        gameState.selectedPiece = e.target;
        gameState.selectedSquare = e.target.parentElement;
        gameState.selectedSquare.classList.add('selected');
    },
    
    // Handle drag end
    handleDragEnd(e) {
        e.target.classList.remove('dragging');
        if (gameState.selectedSquare) {
            gameState.selectedSquare.classList.remove('selected');
        }
        ui.clearSelection();
    },
    
    // Allow dropping
    handleDragOver(e) {
        e.preventDefault();
    },
    
    // Handle drop
    handleDrop(e) {
        e.preventDefault();
        const targetSquare = e.target.closest('.square');
        if (!targetSquare || !gameState.selectedPiece) return;

        // Check if the destination has a piece of the same color
        const destinationPiece = targetSquare.querySelector('.piece').textContent.trim();
        if (destinationPiece !== '') {
            const destinationPieceColor = utils.getPieceColor(destinationPiece);
            const selectedPieceColor = utils.getPieceColor(gameState.selectedPiece.textContent);
            
            if (destinationPieceColor === selectedPieceColor) {
                ui.showStatus('Invalid move! Cannot capture your own piece.', false);
                ui.clearSelection();
                return;
            }
        }

        const fromRow = parseInt(gameState.selectedSquare.dataset.row);
        const fromCol = parseInt(gameState.selectedSquare.dataset.col);
        const toRow = parseInt(targetSquare.dataset.row);
        const toCol = parseInt(targetSquare.dataset.col);

        moveHandler.makeMove(fromRow, fromCol, toRow, toCol, gameState.selectedPiece, targetSquare.querySelector('.piece'));
        ui.clearSelection();
    },
    
    // Start new game
    startNewGame() {
        if (!gameState.isGameOver && !confirm('Are you sure you want to start a new game?')) {
            return;
        }
        location.reload();
    }
};

// Initialize game
document.getElementById('new-game-btn').disabled = gameState.isGameOver;

// Set up event listeners
document.querySelectorAll('.square').forEach(square => {
    square.addEventListener('click', eventHandlers.handleSquareClick);
    square.addEventListener('dragover', eventHandlers.handleDragOver);
    square.addEventListener('drop', eventHandlers.handleDrop);
});

document.querySelectorAll('.piece').forEach(piece => {
    piece.addEventListener('dragstart', eventHandlers.handleDragStart);
    piece.addEventListener('dragend', eventHandlers.handleDragEnd);
});

// Assign the startNewGame to global scope to be used by HTML button
window.startNewGame = eventHandlers.startNewGame;
