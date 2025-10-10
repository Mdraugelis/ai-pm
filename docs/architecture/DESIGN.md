# UI Framework Design Guide

## Overview

This document describes the UI framework and design patterns used in the Geisinger AI Initiatives Inventory application. The framework combines **Mantine UI** with **React Hook Form**, **TanStack Table**, and **Tabler Icons** to create a professional, accessible, and maintainable enterprise application.

## Technology Stack

### Core UI Framework
- **Mantine v8.3.1** - Modern React component library with built-in accessibility
- **React 18.3** - Component framework with hooks
- **TypeScript 5.8** - Type safety throughout the application
- **Vite 7.1** - Fast build tool and development server

### Key Libraries
- **@mantine/core** - Core components (Button, Table, Paper, etc.)
- **@mantine/form** - Form state management with validation
- **@mantine/notifications** - Toast notifications
- **@mantine/dropzone** - File upload with drag-and-drop
- **@mantine/hooks** - Utility hooks for common patterns
- **React Hook Form 7.62** - Advanced form handling with validation
- **@tabler/icons-react 3.34** - Comprehensive icon set (3,000+ icons)
- **React Router DOM 7.8** - Client-side routing

## Design Philosophy

### 1. **Professional & Clean**
- Minimalist aesthetic with purposeful whitespace
- Consistent use of Mantine's design tokens
- Professional color palette (blue primary, semantic colors for status)
- Subtle shadows and borders for depth

### 2. **Component-First Architecture**
- Reusable, self-contained components
- Props-based configuration
- TypeScript interfaces for type safety
- Shared components in `components/shared/` directory

### 3. **Accessibility by Default**
- WCAG 2.1 AA compliance through Mantine
- Semantic HTML elements
- ARIA labels and roles
- Keyboard navigation support

### 4. **Mobile-Responsive**
- Grid system with breakpoints
- Responsive typography
- Touch-friendly hit targets (min 44x44px)
- Scrollable tables for small screens

## Component Patterns

### Form Components

#### Example: Initiative Intake Form

```tsx
import { useForm, Controller } from 'react-hook-form';
import { TextInput, Textarea, Select, Button, Stack } from '@mantine/core';

const IntakeForm: React.FC = () => {
  const { control, handleSubmit, formState: { errors } } = useForm({
    defaultValues: {
      title: '',
      department: '',
      description: ''
    }
  });

  const onSubmit = async (data) => {
    // Handle form submission
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <Stack gap="md">
        <Controller
          name="title"
          control={control}
          rules={{ required: 'Title is required' }}
          render={({ field }) => (
            <TextInput
              {...field}
              label="Initiative Title"
              placeholder="Enter title"
              required
              error={errors.title?.message}
            />
          )}
        />

        <Controller
          name="description"
          control={control}
          render={({ field }) => (
            <Textarea
              {...field}
              label="Description"
              placeholder="Describe the initiative..."
              rows={4}
            />
          )}
        />

        <Button type="submit">Submit</Button>
      </Stack>
    </form>
  );
};
```

**Key Features:**
- React Hook Form for state management
- Controller component for Mantine integration
- Built-in validation with error messages
- Accessible form elements with labels

### Data Tables

#### Example: Initiative Table with Sorting

```tsx
import { Table, Paper, Badge, ActionIcon, ScrollArea } from '@mantine/core';
import { IconEdit, IconEye } from '@tabler/icons-react';

const InitiativeTable: React.FC<{ initiatives: Initiative[] }> = ({ initiatives }) => {
  const STATUS_COLORS = {
    'idea': 'gray',
    'proposal': 'blue',
    'pilot': 'pink',
    'production': 'green',
    'retired': 'dark'
  };

  return (
    <Paper withBorder>
      <ScrollArea>
        <Table highlightOnHover verticalSpacing="sm">
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Title</Table.Th>
              <Table.Th>Owner</Table.Th>
              <Table.Th>Stage</Table.Th>
              <Table.Th>Actions</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {initiatives.map((initiative) => (
              <Table.Tr key={initiative.id}>
                <Table.Td>{initiative.title}</Table.Td>
                <Table.Td>{initiative.program_owner}</Table.Td>
                <Table.Td>
                  <Badge
                    color={STATUS_COLORS[initiative.stage]}
                    variant="light"
                  >
                    {initiative.stage}
                  </Badge>
                </Table.Td>
                <Table.Td>
                  <ActionIcon variant="subtle" color="blue">
                    <IconEdit size={16} />
                  </ActionIcon>
                </Table.Td>
              </Table.Tr>
            ))}
          </Table.Tbody>
        </Table>
      </ScrollArea>
    </Paper>
  );
};
```

**Key Features:**
- Responsive ScrollArea wrapper
- Semantic status badges with color coding
- Hover highlighting for better UX
- Icon-based action buttons

### File Upload Components

#### Example: Document Drop Zone

```tsx
import { Dropzone } from '@mantine/dropzone';
import { Stack, Text, Progress, Card } from '@mantine/core';
import { IconUpload, IconX, IconFileText } from '@tabler/icons-react';

const DocumentDropZone: React.FC = ({ onDrop }) => {
  return (
    <Dropzone
      onDrop={onDrop}
      maxSize={50 * 1024 * 1024} // 50MB
      multiple={true}
      accept={['application/pdf', 'application/msword', 'image/*']}
    >
      <Stack align="center" gap="xl" mih={220}>
        <Dropzone.Accept>
          <IconUpload size={52} color="var(--mantine-color-blue-6)" />
        </Dropzone.Accept>

        <Dropzone.Reject>
          <IconX size={52} color="var(--mantine-color-red-6)" />
        </Dropzone.Reject>

        <Dropzone.Idle>
          <IconFileText size={52} color="var(--mantine-color-gray-6)" />
        </Dropzone.Idle>

        <div>
          <Text size="xl">Drag documents here or click to select</Text>
          <Text size="sm" c="dimmed" mt={7}>
            Accepted: PDF, DOC, DOCX, Images (max 50MB)
          </Text>
        </div>
      </Stack>
    </Dropzone>
  );
};
```

**Key Features:**
- Visual feedback for drag states
- File type and size validation
- Upload progress tracking
- Professional file preview cards

### Notification System

#### Example: Toast Notifications

```tsx
import { notifications } from '@mantine/notifications';
import { IconCheck, IconX, IconAlertCircle } from '@tabler/icons-react';

// Success notification
notifications.show({
  title: 'Success',
  message: 'Initiative created successfully',
  color: 'green',
  icon: <IconCheck size={16} />
});

// Error notification
notifications.show({
  title: 'Error',
  message: 'Failed to save changes',
  color: 'red',
  icon: <IconX size={16} />
});

// Info notification
notifications.show({
  title: 'Draft Saved',
  message: 'Your changes have been auto-saved',
  color: 'blue',
  icon: <IconAlertCircle size={16} />
});
```

**Key Features:**
- Consistent notification style
- Icon integration for quick recognition
- Auto-dismissal with configurable timeout
- Color-coded by severity

## Layout Patterns

### Container & Spacing

```tsx
import { Container, Paper, Stack, Group, Grid } from '@mantine/core';

// Page-level container
<Container size="xl" py="md">
  {/* Content constrained to max-width with vertical padding */}
</Container>

// Card-style container
<Paper p="xl" withBorder>
  {/* White background with border and padding */}
</Paper>

// Vertical stacking with consistent gaps
<Stack gap="md">
  {/* Children stacked vertically with medium gap */}
</Stack>

// Horizontal grouping
<Group justify="space-between" gap="sm">
  {/* Children arranged horizontally */}
</Group>

// Responsive grid
<Grid>
  <Grid.Col span={{ base: 12, md: 6 }}>
    {/* Full width on mobile, half on desktop */}
  </Grid.Col>
</Grid>
```

### Accordion Pattern for Forms

```tsx
import { Accordion, Title, Badge } from '@mantine/core';

<Accordion multiple defaultValue={['basic']} variant="separated">
  <Accordion.Item value="basic">
    <Accordion.Control>
      <Group>
        <Title order={3}>Basic Information</Title>
        <Badge color="red" size="sm">Required</Badge>
      </Group>
    </Accordion.Control>
    <Accordion.Panel>
      {/* Form fields */}
    </Accordion.Panel>
  </Accordion.Item>
</Accordion>
```

## Color & Typography System

### Geisinger Healthcare Brand Colors

Inspired by Geisinger's healthcare design system, this application uses a professional, trustworthy color palette that conveys medical professionalism while maintaining accessibility.

#### Primary Color Palette

**Brand Colors:**
```typescript
// Primary teal/turquoise - Brand identifier and primary CTAs
const PRIMARY_TEAL = '#00A3AD';

// Deep blue - Main headings and navigation
const DEEP_BLUE = '#4A6B8B';

// White - Primary background for clean, medical-grade aesthetics
const WHITE = '#FFFFFF';
```

**Accent Colors:**
```typescript
// Medium blue - Secondary sections and information
const MEDIUM_BLUE = '#3498DB';

// Slate blue/gray - Tertiary elements and subtle sections
const SLATE_BLUE = '#5E7A8E';
```

**Supporting Colors:**
```typescript
// Light gray - Background for content sections
const LIGHT_GRAY = '#F5F5F5';

// Dark gray/charcoal - Body text and primary content
const DARK_GRAY = '#333333';

// Medium gray - Secondary text and subtle elements
const MEDIUM_GRAY = '#666666';
```

#### Color Usage Hierarchy

1. **Primary Actions**: Teal/turquoise (`#00A3AD`) for main CTAs and interactive elements
2. **Section Differentiation**: Different blue tones to distinguish service categories
3. **Text Hierarchy**: Deep blue (`#4A6B8B`) for headlines, dark gray (`#333333`) for body text
4. **Backgrounds**: White (`#FFFFFF`) and light gray (`#F5F5F5`) for content separation

#### Accessibility Considerations

- **High Contrast**: All text/background combinations meet WCAG 2.1 AA standards (minimum 4.5:1 ratio)
- **Color Blindness**: Color is never the only indicator; icons and text labels supplement all color-coded information
- **Clear Visual Hierarchy**: Color differentiation creates intuitive navigation paths
- **Medical-Grade Readability**: Professional healthcare aesthetic with excellent legibility

### Application-Specific Color Mappings

**Status Colors:**
```typescript
const STATUS_COLORS = {
  'idea': 'gray',         // Early stage - #666666
  'proposal': 'cyan',     // Under review - #00A3AD (Geisinger teal)
  'pilot': 'blue',        // Testing phase - #4A6B8B (Geisinger deep blue)
  'production': 'green',  // Active - #10B981
  'retired': 'dark'       // Inactive - #333333
};

const RISK_COLORS = {
  'low': 'green',    // #10B981
  'medium': 'orange', // #F59E0B
  'high': 'red',     // #EF4444
  'unknown': 'gray'  // #666666
};
```

**UI Colors (Mantine Theme Integration):**
- Primary: `cyan.6` (#00A3AD - Geisinger teal)
- Secondary: `blue.7` (#4A6B8B - Geisinger deep blue)
- Success: `green.6` (#10B981)
- Warning: `yellow.6` (#F59E0B)
- Error: `red.6` (#EF4444)
- Info: `blue.6` (#3498DB - Medium blue)
- Dimmed text: `gray.6` (#666666)
- Body text: `dark.9` (#333333)

### Typography

```tsx
// Page titles
<Title order={1} size="h2">Page Title</Title>

// Section headings
<Title order={3}>Section Heading</Title>

// Body text
<Text size="sm">Regular body text</Text>

// Dimmed/secondary text
<Text size="sm" c="dimmed">Secondary information</Text>

// Emphasized text
<Text fw={500}>Medium weight text</Text>
<Text fw={600}>Semi-bold text</Text>
```

## Icon Usage

### Tabler Icons Integration

```tsx
import {
  IconEdit,        // Edit actions
  IconEye,         // View actions
  IconTrash,       // Delete actions
  IconUpload,      // Upload actions
  IconDownload,    // Download actions
  IconCheck,       // Success states
  IconX,           // Error/cancel states
  IconAlertCircle, // Warning/info states
  IconFileText,    // Document icons
  IconChevronUp,   // Sort ascending
  IconChevronDown  // Sort descending
} from '@tabler/icons-react';

// Standard icon size in buttons/badges
<IconEdit size={16} />

// Large icons for empty states
<IconFileText size={48} stroke={1.5} />
```

## Best Practices

### 1. **Consistent Spacing**
Use Mantine's spacing scale:
- `xs` = 10px
- `sm` = 12px
- `md` = 16px (default)
- `lg` = 20px
- `xl` = 24px

### 2. **Responsive Design**
Use responsive props:
```tsx
<Grid.Col span={{ base: 12, sm: 6, md: 4, lg: 3 }}>
  {/* Responsive column sizing */}
</Grid.Col>
```

### 3. **Form Validation**
Always provide clear error messages:
```tsx
rules={{
  required: 'This field is required',
  minLength: { value: 10, message: 'Minimum 10 characters' }
}}
```

### 4. **Loading States**
Show feedback during async operations:
```tsx
<Button loading={isLoading}>
  {isLoading ? 'Saving...' : 'Save'}
</Button>
```

### 5. **Empty States**
Provide helpful messages when no data exists:
```tsx
<Center>
  <Stack align="center">
    <IconFileDescription size={48} color="var(--mantine-color-dimmed)" />
    <Text size="lg" fw={500}>No items found</Text>
    <Text size="sm" c="dimmed">Try adjusting your filters</Text>
  </Stack>
</Center>
```

## Component Library Reference

### Form Components
- `TextInput` - Single-line text input
- `Textarea` - Multi-line text input
- `Select` - Dropdown selection
- `Checkbox` - Boolean checkbox
- `Radio` - Radio button group
- `DateInput` - Date picker
- `NumberInput` - Numeric input with controls

### Layout Components
- `Container` - Page-level container with max-width
- `Paper` - Card-style container
- `Stack` - Vertical layout
- `Group` - Horizontal layout
- `Grid` - Responsive grid system
- `Accordion` - Collapsible sections
- `Tabs` - Tab navigation

### Feedback Components
- `Alert` - Information boxes
- `Badge` - Status indicators
- `Loader` - Loading spinner
- `Progress` - Progress bar
- `Notification` - Toast messages
- `Modal` - Dialog boxes

### Navigation Components
- `Button` - Action buttons
- `ActionIcon` - Icon-only buttons
- `Anchor` - Links
- `Breadcrumbs` - Navigation breadcrumbs
- `Pagination` - Page navigation

### Data Display
- `Table` - Data tables
- `Card` - Content cards
- `Text` - Typography
- `Title` - Headings
- `List` - Bulleted/numbered lists

## File Structure

```
frontend/src/
├── components/
│   ├── shared/           # Reusable components
│   │   └── documents/    # Document handling components
│   ├── forms/            # Form components
│   ├── initiatives/      # Initiative-specific components
│   ├── documents/        # Document library components
│   └── layout/           # Layout components
├── contexts/             # React contexts for state
├── services/             # API and utility services
├── types/                # TypeScript interfaces
└── styles/               # Global styles

```

## Getting Started

### Installation

```bash
npm install @mantine/core @mantine/hooks @mantine/form @mantine/notifications @mantine/dropzone
npm install @tabler/icons-react
npm install react-hook-form
```

### Setup

1. **Wrap your app with MantineProvider and custom Geisinger theme:**

```tsx
import { MantineProvider, createTheme } from '@mantine/core';
import { Notifications } from '@mantine/notifications';
import '@mantine/core/styles.css';
import '@mantine/notifications/styles.css';
import '@mantine/dropzone/styles.css';

// Geisinger healthcare theme
const geisingerTheme = createTheme({
  primaryColor: 'cyan',
  colors: {
    // Custom Geisinger teal
    cyan: [
      '#E6F9FA',
      '#CCF3F5',
      '#99E7EB',
      '#66DBE0',
      '#33CFD6',
      '#00A3AD', // Primary brand color
      '#00828A',
      '#006268',
      '#004145',
      '#002123'
    ]
  },
  fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
  headings: {
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    fontWeight: '600',
    sizes: {
      h1: { fontSize: '2rem', lineHeight: '1.2' },
      h2: { fontSize: '1.5rem', lineHeight: '1.3' },
      h3: { fontSize: '1.25rem', lineHeight: '1.4' }
    }
  },
  defaultRadius: 'md',
  shadows: {
    sm: '0 1px 3px rgba(0, 0, 0, 0.1)',
    md: '0 4px 6px rgba(0, 0, 0, 0.1)',
    lg: '0 10px 15px rgba(0, 0, 0, 0.1)'
  }
});

function App() {
  return (
    <MantineProvider theme={geisingerTheme}>
      <Notifications position="top-right" />
      {/* Your app */}
    </MantineProvider>
  );
}
```

2. **Import Mantine CSS in your entry point:**

```tsx
import '@mantine/core/styles.css';
import '@mantine/notifications/styles.css';
import '@mantine/dropzone/styles.css';
```

3. **Using Geisinger brand colors in components:**

```tsx
// Primary brand color (Geisinger teal)
<Button color="cyan">Primary Action</Button>

// Deep blue for headings
<Title order={1} c="blue.7">Main Heading</Title>

// Status badges with healthcare-appropriate colors
<Badge color="cyan" variant="light">In Review</Badge>
<Badge color="blue" variant="light">Pilot Phase</Badge>
<Badge color="green" variant="light">Active</Badge>
```

## Resources

### Documentation
- [Mantine Documentation](https://mantine.dev/)
- [React Hook Form Documentation](https://react-hook-form.com/)
- [Tabler Icons Gallery](https://tabler.io/icons)

### Example Components
- `IntakeForm.tsx` - Complex multi-section form with validation
- `InitiativeTable.tsx` - Sortable data table with actions
- `DocumentDropZone.tsx` - File upload with progress tracking
- `AncillaryDocumentUpload.tsx` - Complete upload flow with metadata

## Healthcare Design Principles

### Trust & Professionalism
- **Clean aesthetic**: Minimalist design conveys medical-grade quality
- **Professional color palette**: Geisinger teal and blue tones inspire confidence
- **Consistent branding**: Color usage reinforces organizational identity
- **Clear hierarchy**: Information architecture follows healthcare documentation standards

### Accessibility & Compliance
- **WCAG 2.1 AA compliance**: All color combinations meet accessibility standards
- **High contrast ratios**: Minimum 4.5:1 for normal text, 3:1 for large text
- **Multi-modal feedback**: Color + icons + text labels for all status indicators
- **Keyboard navigation**: Full keyboard support for all interactive elements
- **Screen reader friendly**: Semantic HTML and ARIA labels throughout

### Patient-Centered Design
- **Clear communication**: Plain language with medical terminology explained
- **Intuitive navigation**: Familiar patterns reduce cognitive load
- **Error prevention**: Validation and confirmation for critical actions
- **Helpful feedback**: Immediate, actionable error messages and success confirmations

## Version
- Document Version: 1.1
- Last Updated: January 2025
- Framework: Mantine 8.3.1 + React 18.3
- Brand Colors: Geisinger Healthcare-inspired palette

---

**Note:** This design system prioritizes simplicity, accessibility, and developer experience while maintaining professional healthcare aesthetics. Keep components focused and composable. When in doubt, check the Mantine documentation for best practices and ensure all color usage maintains WCAG compliance.
