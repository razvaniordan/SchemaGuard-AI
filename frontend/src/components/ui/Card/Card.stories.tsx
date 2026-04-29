import type { Meta, StoryObj } from '@storybook/react';
import { Button } from '../Button';
import { Card } from './Card';

const meta = {
  title: 'UI/Card',
  component: Card,
  tags: ['autodocs'],
  args: {
    title: 'Fee qualification summary',
    description: 'Overview of the current transaction analysis.',
    children: 'This card will be used to display SchemeGuard AI dashboard information.',
  },
} satisfies Meta<typeof Card>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const WithFooter: Story = {
  args: {
    footer: <Button>View details</Button>,
  },
};