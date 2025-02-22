import streamlit as st
import streamlit.components.v1 as components

def swipeable_card():
    # Initialize session state for tracking likes/dislikes if not exists
    if 'liked_users' not in st.session_state:
        st.session_state.liked_users = []
    if 'disliked_users' not in st.session_state:
        st.session_state.disliked_users = []
    
    # Custom HTML/CSS/JS for the swipeable card
    custom_html = """
    <style>
        .wrapper {
            display: flex;
            flex-direction: column;
            align-items: center;
            max-width: 400px;
            margin: 0 auto;
        }
        .card-container {
            width: 300px;
            height: 400px;
            position: relative;
            margin-bottom: 20px;
        }
        .card {
            width: 100%;
            height: 100%;
            position: absolute;
            transition: transform 0.5s;
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .card-content {
            padding: 20px;
            text-align: center;
        }
        .card img {
            width: 100%;
            height: 250px;
            object-fit: cover;
        }
        .action-buttons {
            display: flex;
            justify-content: center;
            gap: 20px;
            padding: 20px;
            width: 100%;
        }
        .btn {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            border: none;
            cursor: pointer;
            font-size: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: transform 0.2s;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .btn:hover {
            transform: scale(1.1);
        }
        .btn-dislike {
            background-color: #ff4b4b;
            color: white;
        }
        .btn-like {
            background-color: #4BD04B;
            color: white;
        }
    </style>
    
    <div class="wrapper">
        <div class="card-container">
            <div class="card" id="card">
                <div class="card-content">
                    <img src="https://via.placeholder.com/300x250" alt="User Photo">
                    <h2>John Doe</h2>
                    <p>Age: 28</p>
                    <p>Location: New York</p>
                </div>
            </div>
        </div>
        <div class="action-buttons">
            <button class="btn btn-dislike" onclick="handleAction('left')">✕</button>
            <button class="btn btn-like" onclick="handleAction('right')">♥</button>
        </div>
    </div>
    
    <script>
    const card = document.getElementById('card');
    
    function handleAction(direction) {
        const isRight = direction === 'right';
        
        // Animate card off screen
        card.style.transition = 'transform 0.5s';
        card.style.transform = `translateX(${isRight ? '150%' : '-150%'}) rotate(${isRight ? '30deg' : '-30deg'})`;
        
        // Reset card after animation
        setTimeout(() => {
            card.style.transition = 'none';
            card.style.transform = 'none';
            
            // Update Streamlit session state (you'll need to implement this)
            if (isRight) {
                window.parent.postMessage({type: 'like'}, '*');
            } else {
                window.parent.postMessage({type: 'dislike'}, '*');
            }
        }, 500);
    }
    </script>
    """
    
    # Render the component with increased height to accommodate buttons
    components.html(custom_html, height=600)
    
    # Handle like/dislike in Streamlit
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Like"):
            st.session_state.liked_users.append("Current User")
            st.rerun()
    with col2:
        if st.button("Dislike"):
            st.session_state.disliked_users.append("Current User")
            st.rerun()

def main():
    st.title('Tinder-style Swipeable Cards')
    
    # Add some spacing
    st.markdown("<br>", unsafe_allow_html=True)
    
    swipeable_card()
    
    # Display stats in the sidebar
    st.sidebar.title('Stats')
    st.sidebar.write('Liked:', len(st.session_state.liked_users))
    st.sidebar.write('Disliked:', len(st.session_state.disliked_users))

if __name__ == '__main__':
    main()