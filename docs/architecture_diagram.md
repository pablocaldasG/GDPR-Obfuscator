# GDPR Obfuscator – Architecture Diagram

> Note: This diagram uses Mermaid syntax.  
> To preview locally in VS Code, install one of:
> - **Markdown Preview Enhanced**
> - **Markdown Preview Mermaid Support**  
>
> On GitHub, Mermaid diagrams render automatically in `.md` files.

```mermaid
%%{init: {"theme": "base", "themeVariables": { 
    "primaryColor": "#f5f5f5", 
    "primaryTextColor": "#222222", 
    "lineColor": "#444444",
    "fontSize": "14px",
    "edgeWidth": 2,
    "tertiaryColor": "#e0e0e0"
}}}%%

flowchart TD
    subgraph Extract
        A[JSON Input with file_to_obfuscate and pii_field] --> B[Read CSV from S3 or Local]
    end

    subgraph Transform
        B --> C[Obfuscate PII fields with XXX mask]
    end

    subgraph Load
        C --> D[Generate CSV bytestream with descriptive filename]
        D --> E[Upload to S3 or save locally]
    end

    subgraph Main
        A --> F[run_pipeline function]
        F --> B
        F --> C
        F --> D
        F --> E
    end

    style Extract fill:#f5f5f5,stroke:#444444,stroke-width:2px
    style Transform fill:#f5f5f5,stroke:#444444,stroke-width:2px
    style Load fill:#f5f5f5,stroke:#444444,stroke-width:2px
    style Main fill:#f5f5f5,stroke:#444444,stroke-width:2px
