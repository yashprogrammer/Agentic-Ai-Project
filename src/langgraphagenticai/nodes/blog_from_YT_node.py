import re
from src.langgraphagenticai.state.blog_state import BlogState
from youtube_transcript_api import YouTubeTranscriptApi
import logging

class BlogFromYTNode:
    """
    Blog from YouTube logic implementation.
    """

    def __init__(self, model, link):
        self.llm = model
        self.link = link

    
    def transcript_generator(self, state: BlogState) -> dict:
        """
        Processes the input state and generates a blog from a YouTube video.
        """
       

        def extract_video_id(link) -> str:
            """
            Extracts the video ID from a YouTube video link.
            """
            match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", link)
            if match:
                return match.group(1)
            else:
                raise ValueError("Invalid YouTube URL")

        try:
            video_id = extract_video_id(self.link)
            transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
            transcript_text = " ".join([segment["text"] for segment in transcript_data])
            return {"transcript" : transcript_text}
        except Exception as e:
            return {"error": str(e)}
    
    def title_creator(self, state: BlogState) -> dict:
        """
        Processes the input state and generates a title for the blog.
        
        """

        try:
            title = self.llm.invoke(f"generate a Single SEO Friendly Title based on the following transcrpit : {state['transcript']}, Output ONLY the title, without any explanation or additional text")

            return{"title" : title}
        except Exception as e:
            return {"error": str(e)}
        
    def content_creator(self, state: BlogState) -> dict:
        """
        Processes the title with transcript and generates content for the blog.
        """

        try:
            content = self.llm.invoke(f"generate a blog content based on the following transcrpit : {state["transcript"]} and title : {state["title"]}, Output ONLY the content not even title, without any explanation or additional text")
            return{"content": content}
        except Exception as e:
            return {"error": str(e)}    