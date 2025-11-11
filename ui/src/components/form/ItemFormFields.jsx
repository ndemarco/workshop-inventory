import React from 'react'
import { Button, Input, Textarea, Select } from '../UI'

export default function ItemFormFields({
  formValues,
  onChange,
  onExtractSpecs,
  onCheckDuplicates,
  existing
}) {
  return (
    <div className="space-y-6">
      {/* Name & Description */}
      <div>
        <label className="block text-sm font-medium text-gray-900 mb-2">
          Item Name *
        </label>
        <Input
          name="name"
          value={formValues.name}
          onChange={onChange}
          placeholder="e.g., M6 x 50mm Stainless Steel Bolt"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-900 mb-2">
          Description *
        </label>
        <Textarea
          name="description"
          value={formValues.description}
          onChange={onChange}
          placeholder="Detailed description of the item"
          rows={4}
          required
        />
        <div className="mt-2 flex gap-2">
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={onExtractSpecs}
          >
            🔍 Extract Specs
          </Button>
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={onCheckDuplicates}
          >
            ⚠️ Check Duplicates
          </Button>
        </div>
      </div>

      {/* Category & Type */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-900 mb-2">
            Category
          </label>
          <Select
            name="category"
            value={formValues.category}
            onChange={onChange}
            options={existing?.categories || []}
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-900 mb-2">
            Item Type
          </label>
          <Select
            name="item_type"
            value={formValues.item_type}
            onChange={onChange}
            options={existing?.itemTypes || []}
          />
        </div>
      </div>

      {/* Quantity & Unit */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-900 mb-2">
            Quantity
          </label>
          <Input
            type="number"
            name="quantity"
            value={formValues.quantity}
            onChange={onChange}
            min="0"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-900 mb-2">
            Unit
          </label>
          <Select
            name="unit"
            value={formValues.unit}
            onChange={onChange}
            options={existing?.units || ['pieces', 'meters', 'kg', 'liters']}
          />
        </div>
      </div>

      {/* Tags */}
      <div>
        <label className="block text-sm font-medium text-gray-900 mb-2">
          Tags (comma-separated)
        </label>
        <Textarea
          name="tags"
          value={formValues.tags}
          onChange={onChange}
          placeholder="e.g., fastener, metal, stainless-steel"
          rows={2}
        />
      </div>

      {/* Notes */}
      <div>
        <label className="block text-sm font-medium text-gray-900 mb-2">
          Notes
        </label>
        <Textarea
          name="notes"
          value={formValues.notes}
          onChange={onChange}
          placeholder="Additional notes or comments"
          rows={3}
        />
      </div>
    </div>
  )
}