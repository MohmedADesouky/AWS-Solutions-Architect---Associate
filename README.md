# Smart Factory Architecture: Serverless AWS Solution

## Overview

This project provides a comprehensive LaTeX document describing a serverless, fully managed AWS-based Industrial Internet of Things (IIoT) architecture for Global Manufacturing Inc. The architecture spans edge data collection, secure ingestion, purpose-built data storage, analytics and machine learning, and robust security and infrastructure management.

The repository includes:

* **`main.tex`**: The LaTeX source file for the IIoT architecture document.
* **`architecture.png`**: The exported Draw\.io diagram illustrating the service layout and data flows.

## Features

* **Edge Layer**: AWS IoT Greengrass on factory gateways, local Lambda adapters for OPC UA and MQTT.
* **Ingestion & Routing**: AWS IoT Core with SQL-like Rules Engine and AWS Lambda.
* **Data Storage**: Purpose-built databases (Amazon Timestream, AWS IoT SiteWise, AWS IoT Analytics).
* **Analytics & Visualization**: Amazon QuickSight dashboards, AWS IoT Events alerts.
* **Machine Learning**: Amazon SageMaker predictive maintenance models.
* **Security & Management**: AWS IAM, VPC Endpoints, Amazon CloudWatch, AWS CloudFormation/CDK.

## Getting Started

1. **Clone this repository**:

   ```bash
   git clone <your-repo-url>
   cd smart-factory-architecture
   ```

2. **Open in Overleaf**:

   * Create a new project in [Overleaf](https://overleaf.com).
   * Upload `main.tex` and `architecture.png` to the project root.
   * Overleaf will automatically compile the document.

3. **Compile Locally** (optional):

   * Install a LaTeX distribution (TeX Live, MikTeX).
   * Run:

     ```bash
     pdflatex main.tex
     ```

## File Structure

```
├── main.tex          # LaTeX source with detailed architecture description
├── architecture.png  # Diagram of AWS services and data flows
└── README.md         # Project overview and instructions
```

## Customization

* **Diagram**: Modify the Draw\.io source and re-export `architecture.png` to update the figure.
* **Document**: Edit `main.tex` to add sections, update service details, or adjust formatting.

## License

This project is provided under the MIT License. See [LICENSE](LICENSE) for details.

## Acknowledgments

* AWS Official Documentation for service descriptions and best practices.
* Draw\.io for the AWS icon library.
* Global Manufacturing Inc. for the project scenario.

