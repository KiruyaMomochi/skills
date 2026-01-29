---
name: opentelemetry-collector
description: Expert assistance for configuring and understanding OpenTelemetry Collector. Provides guidance on overall architecture and concepts (pipelines, components, data flow), configuring specific receivers, exporters, processors, extensions, and connectors, best practices for deployment and optimization, and troubleshooting common issues. Use this skill when working with OTel Collector configuration or when needing to understand how components work.
---

# OpenTelemetry Collector Expert

## Description
This skill provides comprehensive documentation for **OpenTelemetry Collector**, a vendor-agnostic telemetry data collection and processing platform. It assists with understanding collector architecture, configuring components, and implementing best practices.

## Instructions

### Understanding the Architecture
- **Core Concepts**: The Collector uses a pipeline-based architecture where data flows through receivers → processors → exporters
- **Component Types**:
  - **Receivers**: Collect telemetry data from various sources (traces, metrics, logs)
  - **Processors**: Transform, filter, and enrich telemetry data
  - **Exporters**: Send telemetry data to observability backends
  - **Extensions**: Provide auxiliary capabilities (health checks, auth, etc.)
  - **Connectors**: Connect pipelines, acting as both exporter and receiver

### Configuring Components
- **General Documentation**: Refer to `references/docs/` for architecture, deployment patterns, and configuration fundamentals
- **Component-Specific Docs**: 
  - For receivers: Check `references/components/receiver/[component-name]/README.md`
  - For exporters: Check `references/components/exporter/[component-name]/README.md`
  - For processors: Check `references/components/processor/[component-name]/README.md`
  - For extensions: Check `references/components/extension/[component-name]/README.md`
  - For connectors: Check `references/components/connector/[component-name]/README.md`
- **Configuration Examples**: Most components include example configurations in their README files and `testdata/config*.yaml` files
- **Metadata**: Each component has a `metadata.yaml` file with stability status and supported signals

### Best Practices
- **Configuration Format**: Use YAML format for collector configurations
- **Validation**: Always verify component stability status (alpha/beta/stable) in component metadata
- **Design Patterns**: Review `references/docs/` for deployment patterns (agent vs gateway mode)
- **Resource Management**: Consider memory, CPU, and network requirements when configuring collectors

### Common Patterns
- **Basic Pipeline**: receiver → processor (optional) → exporter
- **Multiple Pipelines**: Different pipelines for traces, metrics, and logs
- **Routing**: Use processors to filter and route data to different exporters
- **Extensions**: Enable health checks, pprof profiling, and authentication

## Available Resources

### General Documentation (`references/docs/`)
- Architecture and concepts
- Installation guides (Kubernetes, Docker, binary)
- Configuration fundamentals
- Deployment patterns (agent, gateway, no-collector)
- Troubleshooting and best practices
- Performance benchmarks

### Component Documentation (`references/components/`)
Over 260 components organized by type:
- **Receivers** (~113): OTLP, Prometheus, host metrics, file logs, cloud-specific (AWS, Azure, GCP), databases, and more
- **Exporters** (~48): OTLP, Prometheus, logging, cloud backends, observability platforms
- **Processors**: Batch, filter, transform, attributes, resource detection, sampling
- **Extensions**: Health check, pprof, authentication, file storage
- **Connectors**: Forward, count, routing between pipelines

### Configuration Examples
- Each component includes example configurations in README
- `testdata/config*.yaml` files contain valid configuration examples
- Check component metadata for stability and supported signals

## Tips
- Start with OTLP receiver/exporter for maximum compatibility
- Use the `batch` processor to optimize performance
- Enable health check extension for monitoring
- Check component stability before production use
- Review official docs for security and production deployment guidance
