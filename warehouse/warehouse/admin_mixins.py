class ReadOnlyEditFieldsMixin():
    """
    Mixing allows the user to specify fields that will be marked as read only in change view
    """

    def get_readonly_fields(self, request, instance=None):
        if instance:
            return self.readonly_edit_fields + self.readonly_fields

        return self.readonly_fields


class ModedInlinesMixin():
    """
    Mixin is responsible for creating two variables available to the user: change_only_inlines and create_only_inlines
    which allow to specify inline admins for change or create views only
    """

    change_only_inlines = ()
    create_only_inlines = ()

    def _construct_inlines(self, all_inlines, target_inlines, obsolete_inlines):
        """

        Method creates new inlines list containing inlines that were specified in target_inlines, and all_inlines,
        but that are not present in obsolete_inlines. Resulting tuple does not allow duplicates
        """
        inlines = ()

        for inline in target_inlines:
            if inline not in all_inlines:
                inlines += (inline,)

        for inline in all_inlines:
            if inline not in obsolete_inlines:
                inlines += (inline,)

        return inlines

    def change_view(self, request, object_id, form_url='', extra_context=None):
        self.inlines = self._construct_inlines(self.inlines, self.change_only_inlines, self.create_only_inlines)

        return super(ModedInlinesMixin, self).change_view(request, object_id, form_url, extra_context)

    def add_view(self, request, form_url='', extra_context=None):
        self.inlines = self._construct_inlines(self.inlines, self.create_only_inlines, self.change_only_inlines)

        return super(ModedInlinesMixin, self).add_view(request, form_url, extra_context)