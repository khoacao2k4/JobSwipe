import streamlit as st
import streamlit.components.v1 as components

def swipeable_card():
    if 'liked_users' not in st.session_state:
        st.session_state.liked_users = []
    if 'disliked_users' not in st.session_state:
        st.session_state.disliked_users = []
    
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
            cursor: pointer;
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

        /* Modal Styles */
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.7);
            z-index: 1000;
            justify-content: center;
            align-items: center;
        }
        .modal-content {
            background-color: white;
            padding: 30px;
            border-radius: 15px;
            max-width: 600px;
            width: 90%;
            max-height: 90vh;
            overflow-y: auto;
            position: relative;
            animation: modalSlideIn 0.3s ease-out;
        }
        @keyframes modalSlideIn {
            from {
                transform: translateY(-50px);
                opacity: 0;
            }
            to {
                transform: translateY(0);
                opacity: 1;
            }
        }
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        .modal-close {
            position: absolute;
            right: 20px;
            top: 20px;
            font-size: 24px;
            cursor: pointer;
            background: none;
            border: none;
            color: #666;
        }
        .modal-close:hover {
            color: #000;
        }
        .modal-image {
            width: 100%;
            max-height: 400px;
            object-fit: cover;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .modal-info {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin-bottom: 20px;
        }
        .info-item {
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 8px;
        }
        .info-label {
            font-weight: bold;
            color: #666;
            font-size: 0.9em;
        }
        .info-value {
            color: #333;
            font-size: 1.1em;
            margin-top: 5px;
        }
        .modal-bio {
            line-height: 1.6;
            color: #444;
            margin-bottom: 20px;
        }
        .modal-interests {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 15px;
        }
        .interest-tag {
            background-color: #e9ecef;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            color: #495057;
        }
    </style>
    
    <div class="wrapper">
        <div class="card-container">
            <div class="card" id="card" onclick="openModal()">
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

    <!-- Modal -->
    <div class="modal" id="userModal">
        <div class="modal-content">
            <button class="modal-close" onclick="closeModal()">×</button>
            <img class="modal-image" src="https://via.placeholder.com/600x400" alt="User Photo">
            
            <h2>John Doe</h2>
            <p class="modal-bio">
                Hey there! 👋 I'm a software engineer by day and a photographer by night. 
                Love exploring new coffee shops and going on spontaneous adventures.
            </p>
            
            <div class="modal-info">
                <div class="info-item">
                    <div class="info-label">Age</div>
                    <div class="info-value">28</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Location</div>
                    <div class="info-value">New York, NY</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Occupation</div>
                    <div class="info-value">Software Engineer</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Education</div>
                    <div class="info-value">NYU</div>
                </div>
            </div>

            <h3>Interests</h3>
            <div class="modal-interests">
                <span class="interest-tag">Photography</span>
                <span class="interest-tag">Coffee</span>
                <span class="interest-tag">Travel</span>
                <span class="interest-tag">Technology</span>
                <span class="interest-tag">Hiking</span>
                <span class="interest-tag">Music</span>
            </div>
        </div>
    </div>
    
    <script>
    const card = document.getElementById('card');
    const modal = document.getElementById('userModal');
    
    function handleAction(direction) {
        const isRight = direction === 'right';
        
        card.style.transition = 'transform 0.5s';
        card.style.transform = `translateX(${isRight ? '150%' : '-150%'}) rotate(${isRight ? '30deg' : '-30deg'})`;
        
        setTimeout(() => {
            card.style.transition = 'none';
            card.style.transform = 'none';
            
            if (isRight) {
                window.parent.postMessage({type: 'like'}, '*');
            } else {
                window.parent.postMessage({type: 'dislike'}, '*');
            }
        }, 500);
    }

    function openModal() {
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }

    function closeModal() {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }

    // Close modal when clicking outside
    modal.addEventListener('click', function(event) {
        if (event.target === modal) {
            closeModal();
        }
    });

    // Close modal on escape key
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            closeModal();
        }
    });
    </script>
    """
    
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
    st.markdown("<br>", unsafe_allow_html=True)
    
    swipeable_card()
    
    st.sidebar.title('Stats')
    st.sidebar.write('Liked:', len(st.session_state.liked_users))
    st.sidebar.write('Disliked:', len(st.session_state.disliked_users))

if __name__ == '__main__':
    main()