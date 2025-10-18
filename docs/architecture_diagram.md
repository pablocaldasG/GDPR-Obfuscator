# GDPR Obfuscator – Architecture Diagram

> Note: This diagram uses Mermaid syntax. To preview locally in VS Code,
> install a Mermaid-compatible Markdown extension such as:
> - Markdown Preview Enhanced
> - Markdown Preview Mermaid Support
> 
> On GitHub, Mermaid diagrams render automatically in `.md` files.

```mermaid
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

    style Extract fill:#f9f,stroke:#333,stroke-width:1px
    style Transform fill:#ff9,stroke:#333,stroke-width:1px
    style Load fill:#9f9,stroke:#333,stroke-width:1px
    style Main fill:#ccf,stroke:#333,stroke-width:1px
