import argparse
import gradio

# Specify mode
parser = argparse.ArgumentParser(description='Start service with different modes.')
parser.add_argument('--langchain', action='store_true')
parser.add_argument('--towhee', action='store_true')

args = parser.parse_args()

USE_LANGCHAIN = args.langchain
USE_TOWHEE = args.towhee

assert (USE_LANGCHAIN and not USE_TOWHEE ) or (USE_TOWHEE and not USE_LANGCHAIN), \
    'The service should start with either "--langchain" or "--towhee".'

if USE_LANGCHAIN:
    from langchain_src.operations import chat, insert, drop, get_history
if USE_TOWHEE:
    from towhee_src.operations import chat, insert, drop, get_history


def respond(session, project, msg):
    chat(session, project, msg)
    history = get_history(project, session)
    return history

def load(url, project):
    return insert(data_src=url, project=project, source_type='url')


if __name__ == '__main__':
    with gradio.Blocks() as demo:
        gradio.Markdown('''<h1><center>Akcio Demo</center></h1>

        ## Build project with document

        1. Name your project (The name can contain numbers, letters, and underscores. It must start with a letter or an underscore.)
        2. Provide document link
        3. Start to load data
        ''')

        with gradio.Column():
            with gradio.Row():
                project = gradio.Textbox(label='project')
                data_file = gradio.Textbox(label='Doc url')
            load_btn = gradio.Button('Load')
            doc_count = gradio.Number(label='count of doc chunks')
            load_btn.click(
                fn=load,
                inputs=[
                    data_file,
                    project
                    ],
                outputs=[
                    doc_count
                ],
            )

            gradio.Markdown('''
            ## Start conversation

            1. Enter your session id (to manage chat history)
            2. Send message to chat with Akcio
            ''')

            session_id = gradio.Textbox(label='session_id')
            conversation = gradio.Chatbot(label='conversation')
            question = gradio.Textbox(label='question', value=None)

            send_btn = gradio.Button('Send')
            send_btn.click(
                fn=respond,
                inputs=[
                    session_id,
                    project,
                    question
                ],
                outputs=[
                    conversation
                ],
            )
            clear_btn = gradio.Button('Clear')
            clear_btn.click(lambda: None, None, conversation, queue=False)

    demo.launch(share=True)

