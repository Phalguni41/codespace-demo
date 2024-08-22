import React, { useState } from 'react';
import axios from 'axios';

function App() {
    const [prompt, setPrompt] = useState('');
    const [projectName, setProjectName] = useState('');
    const [repoUrl, setRepoUrl] = useState('');
    const [codespaceUrl, setCodespaceUrl] = useState('');
    const [message, setMessage] = useState('');

    // Handle project generation
    const handleGenerateProject = async () => {
        try {
            const response = await axios.post('http://localhost:8000/generate_project/', {
                prompt,
                project_name: projectName
            });
            setMessage(response.data.message);
            setCodespaceUrl(response.data.codespace_url);
        } catch (error) {
            console.error("Error generating project:", error.response ? error.response.data.detail : error.message);
            setMessage("Error generating project. Please check the console for details.");
        }
    };

    // Handle opening in Codespaces
    const handleOpenInCodespaces = async () => {
        try {
            const response = await axios.get('http://localhost:8000/open_in_codespaces/', {
                params: { project_name: projectName }
            });
            setCodespaceUrl(response.data.codespace_url);
        } catch (error) {
            console.error("Error opening in Codespaces:", error.response ? error.response.data.detail : error.message);
            setMessage("Error opening in Codespaces. Please check the console for details.");
        }
    };

    // Handle opening an existing repository in Codespaces
    const handleOpenExistingRepo = async () => {
        try {
            const response = await axios.post('http://localhost:8000/open_existing_repo/', {
                repo_url: repoUrl
            });
            setCodespaceUrl(response.data.codespace_url);
        } catch (error) {
            console.error("Error opening existing repository:", error.response ? error.response.data.detail : error.message);
            setMessage("Error opening existing repository. Please check the console for details.");
        }
    };

    return (
        <div style={{ textAlign: 'center', marginTop: '50px' }}>
            <h1>Generate and Open Project</h1>
            
            <h2>Generate New Project</h2>
            <input
                type="text"
                value={projectName}
                onChange={(e) => setProjectName(e.target.value)}
                placeholder="Enter project name"
                style={{ width: '300px', padding: '8px' }}
            />
            <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Enter project prompt"
                rows="4"
                style={{ width: '300px', padding: '8px', marginTop: '10px' }}
            />
            <br />
            <button onClick={handleGenerateProject} style={{ marginTop: '10px', padding: '8px 16px' }}>
                Generate Project
            </button>
            <button onClick={handleOpenInCodespaces} style={{ marginTop: '10px', padding: '8px 16px' }}>
                Open in Codespaces
            </button>

            <h2>Open Existing Repository</h2>
            <input
                type="text"
                value={repoUrl}
                onChange={(e) => setRepoUrl(e.target.value)}
                placeholder="Enter GitHub repo URL"
                style={{ width: '300px', padding: '8px' }}
            />
            <br />
            <button onClick={handleOpenExistingRepo} style={{ marginTop: '10px', padding: '8px 16px' }}>
                Open Existing Repo in Codespaces
            </button>

            {message && <p>{message}</p>}
            {codespaceUrl && (
                <p>
                    <a href={codespaceUrl} target="_blank" rel="noopener noreferrer">
                        Open in GitHub Codespaces
                    </a>
                </p>
            )}
        </div>
    );
}

export default App;
