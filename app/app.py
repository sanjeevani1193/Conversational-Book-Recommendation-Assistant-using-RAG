import json
import streamlit as st

from src.embedder import load_embedding_model
from src.explainer import explain_recommendations
from src.pipeline import get_recommendations


def is_no_change(text: str) -> bool:
    no_change_values = {
        "",
        "no",
        "nope",
        "n",
        "none",
        "nothing",
        "nah",
        "no changes",
        "no more changes",
        "no other changes",
        "no extra preferences",
        "no preference changes",
        "no preferences",
    }
    return text.strip().lower() in no_change_values


def build_final_query(base_query: str, preferences: list[str]) -> str:
    if not preferences:
        return base_query
    return f"{base_query}. Extra preferences: {'; '.join(preferences)}"


@st.cache_resource
def get_model():
    return load_embedding_model()


def init_session_state():
    defaults = {
        "session_started": False,
        "session_finished": False,
        "base_query": "",
        "preferences": [],
        "result": None,
        "show_details": True,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_session():
    st.session_state.session_started = False
    st.session_state.session_finished = False
    st.session_state.base_query = ""
    st.session_state.preferences = []
    st.session_state.result = None
    st.session_state.initial_query_input = ""
    st.session_state.initial_preferences_input = ""
    st.session_state.followup_input = ""


def run_recommendation_search():
    model = get_model()
    final_query = build_final_query(
        st.session_state.base_query,
        st.session_state.preferences
    )

    result = get_recommendations(
        user_query=final_query,
        model=model,
        explain_fn=explain_recommendations,
    )

    st.session_state.result = result


def start_new_conversation():
    base_query = st.session_state.get("initial_query_input", "").strip()
    initial_preferences = st.session_state.get("initial_preferences_input", "").strip()

    if not base_query:
        st.warning("Please enter what kind of book you're looking for.")
        return

    st.session_state.base_query = base_query
    st.session_state.preferences = []

    if initial_preferences and not is_no_change(initial_preferences):
        st.session_state.preferences.append(initial_preferences)

    st.session_state.session_started = True
    st.session_state.session_finished = False

    with st.spinner("Finding recommendations..."):
        run_recommendation_search()


def refine_conversation():
    followup = st.session_state.get("followup_input", "").strip()

    if not followup:
        st.warning("Type a new preference, or click 'No More Changes'.")
        return

    if is_no_change(followup):
        st.session_state.session_finished = True
        return

    st.session_state.preferences.append(followup)

    with st.spinner("Updating recommendations..."):
        run_recommendation_search()

    st.session_state.followup_input = ""


def end_conversation():
    st.session_state.session_finished = True


def render_search_summary():
    st.subheader("Current Request")
    st.markdown(f"**Base query:** {st.session_state.base_query}")

    if st.session_state.preferences:
        st.markdown("**Preferences added so far:**")
        for i, pref in enumerate(st.session_state.preferences, start=1):
            st.markdown(f"{i}. {pref}")
    else:
        st.markdown("**Preferences added so far:** None")

    st.markdown("**Final retrieval query:**")
    st.code(
        build_final_query(st.session_state.base_query, st.session_state.preferences),
        language=None
    )


def render_debug_details(result: dict):
    if not result:
        return

    st.subheader("Parsed Query")
    st.json(result.get("parsed_query", {}))

    st.subheader("Search Queries")
    for q in result.get("search_queries", []):
        st.markdown(f"- {q}")

    st.subheader("Pipeline Stats")
    st.json(result.get("stats", {}))


def render_book_card(book: dict, rank: int):
    st.markdown("---")
    st.markdown(f"### {rank}. {book.get('title', 'Unknown Title')}")

    col1, col2 = st.columns([1, 3])

    with col1:
        cover_url = book.get("cover_url", "")
        if cover_url:
            st.image(cover_url, use_container_width=True)
        else:
            st.caption("No cover available")

    with col2:
        st.markdown(f"**Author:** {book.get('author', 'Unknown')}")
        st.markdown(f"**Source:** {book.get('source', 'Unknown')}")
        st.markdown(f"**Published year:** {book.get('published_year', 'N/A')}")
        st.markdown(f"**Categories:** {book.get('categories', 'N/A')}")
        if book.get("isbn"):
            st.markdown(f"**ISBN:** {book.get('isbn')}")

        description = (book.get("description") or "").strip()
        if description:
            short_desc = description[:500] + ("..." if len(description) > 500 else "")
            st.markdown(f"**Description:** {short_desc}")

        st.markdown(
            f"**Semantic score:** {book.get('similarity_score', 0):.4f}  \n"
            f"**Final score:** {book.get('final_score', 0):.4f}"
        )

        if book.get("info_link"):
            st.markdown(f"[Open book link]({book['info_link']})")


def render_results():
    result = st.session_state.result

    if not result:
        return

    render_search_summary()

    if st.session_state.show_details:
        render_debug_details(result)

    st.subheader("Top Recommendations")
    top_books = result.get("top_books", [])

    if not top_books:
        st.info("No usable books found for this request.")
    else:
        for i, book in enumerate(top_books, start=1):
            render_book_card(book, i)

    st.subheader("Why These Match")
    explanation = result.get("explanation", "").strip()
    if explanation:
        st.write(explanation)
    else:
        st.info("No explanation available.")


def render_followup_section():
    if not st.session_state.session_started or st.session_state.session_finished:
        return

    st.markdown("---")
    st.subheader("Continue the Conversation")
    st.write("Add another preference to refine the recommendations, or end the session.")

    st.text_input(
        "Add more preferences",
        key="followup_input",
        placeholder="Examples: more psychological, no fantasy, slower burn, more angst"
    )

    col1, col2 = st.columns(2)

    with col1:
        st.button(
            "Refine Recommendations",
            use_container_width=True,
            on_click=refine_conversation
        )

    with col2:
        st.button(
            "No More Changes",
            use_container_width=True,
            on_click=end_conversation
        )


def render_finished_section():
    if not st.session_state.session_finished:
        return

    st.markdown("---")
    st.success("Session ended.")
    st.write("You can start a fresh search anytime.")

    st.button("Start New Search", use_container_width=True, on_click=reset_session)


def main():
    st.set_page_config(
        page_title="Conversational Book Recommendation Assistant",
        page_icon="📚",
        layout="wide",
    )

    init_session_state()

    st.title("📚 Conversational Book Recommendation Assistant")
    st.write(
        "Describe the kind of book you want, get recommendations, and keep refining them through follow-up preferences."
    )

    st.session_state.show_details = st.checkbox(
        "Show parsed tags and search details",
        value=st.session_state.show_details
    )

    if not st.session_state.session_started:
        st.text_area(
            "What kind of book are you looking for?",
            key="initial_query_input",
            placeholder="Example: a girl who gets kidnapped falls in love with her kidnapper",
            height=120,
        )

        st.text_input(
            "Extra preferences",
            key="initial_preferences_input",
            placeholder="Example: darker tone, more psychological, no fantasy"
        )

        st.button(
            "Get Recommendations",
            on_click=start_new_conversation
        )

    if st.session_state.session_started:
        render_results()
        render_followup_section()
        render_finished_section()


if __name__ == "__main__":
    main()